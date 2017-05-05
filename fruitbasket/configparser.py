import ConfigParser
import os

# Configuration files will always be relative to the parser file
# Instead of attemping to find the path settings/application.conf relative to the file that made the call
parserpath = os.path.dirname(os.path.abspath(__file__))
settingspath = os.path.join(parserpath, 'settings')

CONFIG_FILES = ['configuration.conf']

# Only necessary to update the file name, this will append the correct path to each
for i, f in enumerate(CONFIG_FILES):
    CONFIG_FILES[i] = os.path.join(settingspath, f)


config = ConfigParser.SafeConfigParser()


def readfile(name):
    filename = name + '.conf'
    filepath = os.path.join(settingspath, filename)

    if filepath not in CONFIG_FILES:
        print 'not here boss'
        return 1

    config.read(filepath)


def value(section, option, name='configuration'):
    readfile(name)

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


def setvalue(section, option, value, name='configuration'):
    readfile(name)

    if config.has_section(section):
        if config.has_option(section, option):
            value = config.set(section, option, value)

            with open(CONFIG_FILES[0], 'wb') as configfile:
                config.write(configfile)

            return value
        else:
            print 'No Option: %s Exists' % option
            return None
    else:
        print 'No Section: %s Exists' % section
        return None


def get_sections(name='configuration'):
    readfile(name)
    return config.sections()
