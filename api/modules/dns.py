import time
import logging
import tempfile
import subprocess
import collections
import blockstack_zones

logger = logging.getLogger(__name__)


class InvalidZoneFile(Exception):
    pass


class DNSUtils():

    default_ttl = 3600
    default_soa = {
        "mname": "dns0.easydns.com.",
        "rname": "zone.easydns.com.",
        "refresh": 43200,
        "retry": 10800,
        "expire": 1209600,
        "minimum": 300,
    }
    default_ns_records = [
        {"host": "adns1.easydns.com."},
        {"host": "adns2.easydns.com."},
    ]

    def map_name(self, rr_type, field):
        """
        Map field name in database to field name for blockstack_zones
        """
        if field == "hostname":
            return "name"
        elif rr_type in ["A", "AAAA"] and field == "value":
            return "ip"
        elif (rr_type == "MX" or rr_type == "NS") and field == "value":
            return "host"
        elif rr_type == "MX" and field == "priority":
            return "preference"
        elif rr_type == "TXT" and field == "value":
            return "txt"
        elif rr_type == "CNAME" and field == "value":
            return "alias"
        elif rr_type == "SRV" and field == "value":
            return "target"

        # Provide the original field name if no custom mapping found
        return field

    def prepare_records_for_zone_file(self, website, records):
        """
        Take a list of Record objects for a website and preprocess them for the zone file.
        The records should return as a dict with the correct names for use by blockstack-zones.
        """
        record_data = self.remap_records_for_zone_file(records)
        record_data = self.add_default_records(website, record_data)
        return self.rewrite_records(website, record_data)

    def rewrite_records(self, website, record_data):
        """
        Rewrite mail records so that they work when the root domain is behind Deflect.

        Need to fix:
        - All records with no label set (should default to @)
        - mail. CNAMEs pointing to apex domain
        - MX records for the root domain.
        """
        updated_records = collections.defaultdict(list)
        for record_type in record_data:
            for record in record_data[record_type]:
                if not record["name"]:
                    record["name"] = "@"

                # Check if this record is a mail. CNAME point to the apex domain.
                if (record_type == "cname" and record["name"] == "mail" and
                        record["alias"] == "{}.".format(website.url)):
                    # Replace this CNAME record with an A record
                    updated_records["a"].append({"name": "mail", "ip": website.ip_address})
                    continue  # Do not add the original cname record

                elif record_type == "mx" and record["host"] == "{}.".format(website.url):
                    # Only add A record if 'deflectmx' record does not already exist.
                    if not [r for r in record_data["a"] if r["name"] == "deflectmx"]:
                        updated_records["a"].append({"name": "deflectmx", "ip": website.ip_address})
                    else:
                        logger.info("A deflectmx already exists")

                    # Rewrite the MX record to point to deflectmx.WEBSITE
                    record["host"] = "deflectmx.{}.".format(website.url)

                updated_records[record_type].append(record)
        return updated_records

    def add_default_records(self, website, record_data):
        """
        Add the default origin DNS records which are created by Deflect
        """
        if website.ip_address:
            record_data.setdefault("a", []).append({"name": "@", "ip": website.ip_address})
        record_data.setdefault("cname", []).append({"name": "www", "alias": website.url + "."})
        return record_data

    def remap_records_for_zone_file(self, records):
        """
        Remap input to be in the correct structure for blockstack_zones's `make_zone_file`.
        """
        record_data = collections.defaultdict(list)
        record_fields = ['hostname', 'value', 'priority', 'weight', 'port', 'ttl']

        for record in records:
            data = {}
            for field in record_fields:
                field_value = getattr(record, field)
                if field_value is not None:
                    # Map field name to the name expected by blockstack_zones
                    data[self.map_name(record.type, field)] = field_value
            record_data[record.type.lower()].append(data)

        return record_data

    def create_and_validate_zone_file(self, website, records):
        """
        Take a list of Record row objects, adds necessary placeholders and validates zone

        Returns the zone file or raises an InvalidZoneFile exception.
        """
        record_data = self.prepare_records_for_zone_file(website, records)

        # Fill in placeholder fields to create a full zone which can be validated
        record_data["ttl"] = self.default_ttl
        record_data["soa"] = self.default_soa
        record_data["soa"]["serial"] = int(time.time())
        record_data["ns"] += self.default_ns_records
        zone_file = blockstack_zones.make_zone_file(record_data, origin=(website.url + "."),
                                                    ttl=self.default_ttl)

        if self.validate_zone_file(origin=website.url, zone_data=zone_file):
            return zone_file

    def validate_zone_file(self, origin, zone_data):
        """
        Call named-checkzone to validate the entered DNS records.
        """
        with tempfile.NamedTemporaryFile(mode='w') as zone_file:
            # Write the zone file to a temporary location
            zone_file.write(zone_data)
            zone_file.flush()

            logger.debug("Validating zone file:\n%s", zone_data)

            try:
                output = subprocess.check_output(["named-checkzone", origin, zone_file.name],
                                                stderr=subprocess.STDOUT)
                logger.info("Zone for %s validated successfully: \n%s", origin, output)
                return True

            except subprocess.CalledProcessError as err:
                logger.error("Invalid zone for %s:\n%s \nZone:\n%s", origin, err.output,
                                        zone_data)
                raise InvalidZoneFile(err.output)
            except OSError:
                logger.exception("bind-checkzone must be installed to validate DNS "
                                            "records.")
                raise
            finally:
                zone_file.close()
