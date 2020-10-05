import six
import yaml

from django.db import models
from django.core.exceptions import ValidationError
from yamlfield.fields import YAMLField
from deepdiff import DeepDiff


class BadYaml(ValidationError):
    pass

class CustomYAMLField(YAMLField):
    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert our YAML string to a Python object
        after we load it from the DB.
        """
        if value == "":
            return None
        try:
            if isinstance(value, six.string_types):
                return yaml.load(value, Loader=yaml.FullLoader)
        except ValueError:
            raise BadYaml("Fail to load invalid YAML in diff field")
        return value

class YamlDiff(models.Model):
    """
    Note we're using the timestamp from the filename and not from
    the "timestamp" key within the file.
    """
    class Meta:
        app_label = "api"

    # epoch_time = db.Column(db.BigInteger)
    epoch_time = models.BigIntegerField()

    # prev_epoch_time = db.Column(db.BigInteger)
    prev_epoch_time = models.BigIntegerField()

    # diff = db.Column(YAMLEncodedDict)
    diff = CustomYAMLField()

    # partition = db.Column(db.String(150), default="")
    partition = models.CharField(max_length=150, default='', null=True, blank=True)

    @classmethod
    def create(cls, old_timestamp, new_timestamp, old_config, new_config, partition=""):
        """
        Replacement of __init__ in SQLAlchemy

        YamlDiff(old_timestamp_s, new_timestamp_s,
                 old_config_dict, new_config_dict,
                 output_directory)
        """

        if "remap" not in old_config:
            raise BadYaml("d1 doesen't have 'remap' key")
        if "remap" not in new_config:
            raise BadYaml("d2 doesen't have 'remap' key")

        diff = dict(DeepDiff(
            old_config["remap"], new_config["remap"], ignore_order=True))

        yaml_diff = cls(
            prev_epoch_time=old_timestamp,
            epoch_time=new_timestamp,
            diff=yaml.dump(diff),
            partition=partition)

        return yaml_diff, diff

    def __repr__(self):
        return '<YamlDiff partition={}, epoch_time={}, prev_epoch_time={}>'.\
                format(self.partition, self.epoch_time, self.prev_epoch_time)

    def __str__(self):
        return 'YamlDiff partition={}, epoch_time={}, prev_epoch_time={}'.\
                format(self.partition, self.epoch_time, self.prev_epoch_time)
