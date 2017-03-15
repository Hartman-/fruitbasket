import ConfigParser
import os

CONFIG_FILES = ['settings/applications.conf']

config = ConfigParser.SafeConfigParser()


def readfile():
    config.read(CONFIG_FILES)


def get_config_value(section, option):
    readfile()

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.get(section, option)
            return value
        else:
            print 'No Option: %s Exists' % option
            return None
    else:
        print 'No Section: %s Exists' % section
        return None


def get_sections():
    readfile()
    return config.sections()


if __name__ == "__main__":
    print get_config_value('nuke', 'exe')
