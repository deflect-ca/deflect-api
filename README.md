# Deflect API

This project serves as the API interface to Deflect. Several components are integrated within this project including edgemanage, a database for storing DNS and website records, as well as the API and gen_site_config module.

## System diagram

![system-diagram-new](https://user-images.githubusercontent.com/1984426/164418270-0fddc429-29e5-4e4d-be2f-664f6ead708d.jpg)

## Overview

- Deflect-API is based on Django framework
- Uses MySQL as database to store:
  - Website list (URL, origin IP)
  - Website options and config
  - DNS records
  - Client certs
  - Edge (IP, hostname, dnet)
  - Dnet
- gen_site_config script (django command line script) generates site.yml according to database
- Provides an HTTP API to interact with database
- Provides an Web interface to interact with database (django admin)
- Works with one submodules (highlighted in the diagram above)
  - edgemanage3
- edgemanage3:
  - python integration
  - feature:
    - edge_query: query edge status
    - edge_conf: configure edge
    - edge_manage: cronjob to execute every min


## Integration

Deflect-API has several integration mechanisms in place. This table is a breif overview of how everything works together:

verb    | subject       | 1st reaction         | 2nd reaction
--------| --------------|----------------------|-------------------------
CD[1]   | website[3]    | `gen_site_config`    |
U[2]    | website       | `gen_site_config`    |
CU      | edge          | edgemanage update[4] |
D       | edge          | edgemanage update    | `docker prune`
C       | dnet          | edgemanage update    |
D       | dnet          | edgemanage update    |

In this table, subject could represent HTTP API endpoints, or operations via django admin. Once the action of the verb, for example, C (create), is committed, the 1st reaction will be triggered right-away. Depending on the category, the second reaction will be triggered after the first reaction is complete.

Most long running task are triggered by a celery worker, such as `gen_site_config`. This could be config in `.env` by setting `GSC_TRIGGER_UPON_DB_CHANGE`

Footnotes:

1. CD: Create(C) and Delete(D)
2. U: Update(U)
3. website: Websites, Website Options, DNS records and certificates
4. edgemanage update: files under `edgelist_dir` is updated according to latest database changes of dnet and edges

## Provisioning and Deployment

Please refer to [INSTALL.md](docs/INSTALL.md)

## Usage

### API Documentation

Please refer to [HTTP API Documentation](https://equalitie.github.io/deflect-core/)

### Django command line

#### **gen_site_config**

Generate `site.yml` file according to `Website`, `WebsiteOption` and `Record` model

    python manage.py gen_site_config --output <path> --blacklist <list.txt> --debug

Configuration should be set in `.env` before running this command:

    GSC_LOG_FILE=/var/tmp/gen_site_config.log
    GSC_OUTPUT_LOCATION=/var/www/brainsconfig
    GSC_PARTITIONS={"part1": {"dnets": ["dnet1"]}, "part2": {"dnets": ["dnet2"]}}
    GSC_DEFAULT_NETWORK=dnet1
    GSC_IGNORE_APPROVAL=True

`GSC_IGNORE_APPROVAL` ignores `approval` in `website_option` during `gen_site_config`, this should be set to `True` in most cases.

For dev purposes, `GSC_LOG_FILE` and `GSC_OUTPUT_LOCATION` could make use of the `dev/gen_sit_config` directory.

### Tests

Invoke django test. Test includes API, Model and gen_site_config test, this will read your local `.env` file. For CircleCI tests, please refer to config in `.circleci`, test coverage report is also generated with automate test.

    python manage.py test

### Django Admin

Built-in admin interface can be accessed via [http://localhost:8000/admin](http://localhost:8000/admin)

### REST framework GUI

REST framework provides built-in GUI for API testing, auth is required by clicking "Log in" on the top right corner when accessed via [http://localhost:8000/api](http://localhost:8000/api)
