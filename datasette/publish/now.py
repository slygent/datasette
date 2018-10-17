from datasette import hookimpl
import click
from subprocess import call

from .common import (
    add_common_publish_arguments_and_options,
    fail_if_publish_binary_not_installed,
)
from ..utils import temporary_docker_directory


@hookimpl
def publish_subcommand(publish):
    @publish.command()
    @add_common_publish_arguments_and_options
    @click.option(
        "-n",
        "--name",
        default="datasette",
        help="Application name to use when deploying",
    )
    @click.option("--force", is_flag=True, help="Pass --force option to now")
    @click.option("--token", help="Auth token to use for deploy (Now only)")
    @click.option("--spatialite", is_flag=True, help="Enable SpatialLite extension")
    @click.option("--alias", help="Alias URL")
    @click.option("--public", is_flag=True, help="Public?")
    @click.option("--unzip", is_flag=True, help="Unzip file to get sqlite database")
    def now(
        files,
        metadata,
        extra_options,
        branch,
        template_dir,
        plugins_dir,
        static,
        install,
        version_note,
        title,
        license,
        license_url,
        source,
        source_url,
        name,
        force,
        token,
        spatialite,
        alias,
        public,
        unzip,
    ):
        fail_if_publish_binary_not_installed("now", "Zeit Now", "https://zeit.co/now")
        if extra_options:
            extra_options += " "
        else:
            extra_options = ""
        extra_options += "--config force_https_urls:on"

        if alias:
            now_json = '''{
    "features": {
        "cloud": "v1"
    },
    "alias": "''' + alias + '''"
}
'''
        else:
            now_json = '''{
    "features": {
        "cloud": "v1"
    }
}
'''
        
        with temporary_docker_directory(
            files,
            name,
            metadata,
            extra_options,
            branch,
            template_dir,
            plugins_dir,
            static,
            install,
            spatialite,
            version_note,
            unzip,
            {
                "title": title,
                "license": license,
                "license_url": license_url,
                "source": source,
                "source_url": source_url,
            },
        ):
            open('now.json', 'w').write(now_json)
            args = []
            if force:
                args.append("--force")
            if token:
                args.append("--token={}".format(token))
            if public:
                args.append("--public")
            if args:
                call(["now", "--no-verify"] + args)
            else:
                call(["now", "--no-verify"])

            if alias:
                call(["now", "alias"])
