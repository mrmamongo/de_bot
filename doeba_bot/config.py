
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DOEBA_BOT",
    settings_files=['../settings.json', '../.secrets.json'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
