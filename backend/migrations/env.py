""" 
Konfigurační soubor Alembic pro spousteni databazovych migraci ve Flask aplikaci.
Integruje Flask-Migrate (SQLAlchemy) s Alembic; podporuje online i offline rezim.
"""
import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# Alembic Config objekt -- poskytuje pristup k hodnotam z alembic.ini
config = context.config

# Nastaveni loggeru dle konfigurace v alembic.ini
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    # Vrati SQLAlchemy engine z Flask-Migrate extension.
    try:
        # Flask-SQLAlchemy < 3 a Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Flask-SQLAlchemy >= 3
        return current_app.extensions['migrate'].db.engine


def get_engine_url() -> str:
    # Vrati URL pripojeni k databazi jako retezec.
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')                          # Zdvojuje znaky '%' kvuli kompatibilite s ConfigParser formatem v alembic.ini.
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Nastaveni URL databaze do Alembic konfigurace (nutne pred run_migrations_*)
config.set_main_option('sqlalchemy.url', get_engine_url())

# Reference na SQLAlchemy db objekt pro ziskani metadat modelu
target_db = current_app.extensions['migrate'].db


def get_metadata():
    # SQLAlchemy MetaData obsahujici definice tabulek (modelu)
    if hasattr(target_db, 'metadatas'):
        # Flask-SQLAlchemy s vice bindy -- pouzijeme vychozi (None) metadata
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    # Spusti migrace offline bez aktivniho pripojeni k DB
    # Alembic vygeneruje SQL skript který lze spustit manualne (URL staci)
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Spusti migrace online s pripojenim k DB
    # pripoji se a aplikuje vsechny cekajici migrace

    def process_revision_directives(context, revision, directives):
        # Zamezeni generovaní prázdných migrací, pokud autogenerate nedetekuje zadne zmeny
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                # Zadne zmeny -- zrusime generovani prazdneho souboru
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = dict(current_app.extensions['migrate'].configure_args)

    # Registrujeme callback jen pokud jiz neni nastaveny zvenci
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    # Vychozi volby pro porovnavani schematu (nastavime jen kdyz jeste nejsou)
    conf_args.setdefault("compare_type", True)
    conf_args.setdefault("compare_server_default", True)
    conf_args.setdefault("render_as_batch", False)

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


# vyber rezimu, zda Alembic bezi offline nebo online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
