"""
# Thinking out Loud =====

Name parts...
   [SHOW]: Show
    [SEQ]: Sequence
   [SHOT]: Shot
  [STAGE]: Stage (integer)
    [TAG]: Description Tag
[VERSION]: Version (v0001, always padding 4)
   [USER]: Username
    [EXT]: File extension
Common Naming conventions...

- Working Scene file:
[SEQ]_[SHOT]_[TAG]_[STAGE]_[VERSION]_[USER].[EXT]

# Core =====

This module defines core classes to handle operations of setting up the application, environment, and launching into applications.
- class: Setup
- class: Environment
- class: Application
"""

# Import python libraries / modules
import getpass
import glob
from operator import itemgetter
import os
import platform
import psutil
import shutil
import subprocess

# Import Fruitbasket modules
import configparser as config


class Setup(object):
    """
    # SETUP

    Defines basic methods for handling common structure methods.

    """
    def __init__(self, environment):
        # initialize the environment for LAWncher
        self.env = environment

        # self.checkRootPaths()

    def checkRootPaths(self):
        """

        Checks the root paths defined in configuration.json.

        :return: Dict of bools defining success of local/server checks.
        """
        root_data = config.rootSettings()
        root_paths = root_data['paths']

        results = {}

        for key in root_paths:
            results[key] = True
            if not os.path.isdir(root_paths[key]):
                results[key] = False

        return results

    def setRootSetting(self, set_path, value):
        """
        Sets a root setting in configuration.conf.

        :param set_path: List, path of keys leading to the value to set.
        :param value: Value to set.
        :return: Returns set value.
        """

        key_path = ['default', 'root']
        for key in set_path:
            key_path.append(key)

        config.updateJson(key_path, value, resolveRef=False)
        return value

    def createBaseStructure(self, server=True):
        """
        Creates folder structure for the current SHOW.

        :param server: Default True, determines where to build the folders, server or local root.
        :return: 0
        """

        root = self.env.rootserver()
        if server is not True:
            root = self.env.rootlocal()

        show_path = os.path.join(root, self.env.SHOW)

        json_str = 'folders.%s.json' % self.env.SHOW

        data = config.readJson(json_str)
        rel_paths = config.folderPaths(data)
        for rel_path in rel_paths:
            full_path = os.path.join(show_path, rel_path)
            config.createDir(full_path)
        return 0

    def setupShow(self, show):
        """
        Copies necessary files to enable show-based settings. Sets up default applications.

        :param show: Show in which to setup.
        :return: Name of Show.
        """

        default_name = 'folders.default.json'
        default_path = config.fullJsonPath(default_name)

        new_name = 'folders.%s.json' % str(show).lower()
        new_path = config.fullJsonPath(new_name)

        shutil.copy(default_path, new_path)

        # Setup the show to use the default application settings
        self.setShowApps(show)
        return show

    def setShowApps(self, show, show_data=None):
        """
        Sets values for applications. If show_data is left None, references default values.

        :param show: Show to set values for.
        :param show_data: Optional dict to pass in to set application values.
        :return: None
        """

        # base string, need to add application name to complete the reference
        ref_string = "#/default/apps/"

        # return the default application json data
        json_file = config.supportedApplications(keys=False, includePath=True, resolveRef=False)
        json_data = json_file[0]

        if show_data is not None and type(show_data) is dict:
            data_keys = json_data.keys()
            for data_key in data_keys:
                if data_key in show_data:
                    key_path = list(json_file[1])
                    key_path[0] = show

                    key_path.append(str(data_key))
                    for app_key in show_data[data_key]:
                        full_path = list(key_path)
                        full_path.append(app_key)

                        config.updateJson(full_path, show_data[data_key][app_key], resolveRef=False)

                else:
                    key_path = list(json_file[1])
                    key_path[0] = show

                    key_path.append(str(data_key))
                    key_path.append('$ref')

                    full_ref = ref_string + data_key

                    config.updateJson(key_path, full_ref, resolveRef=False)

        # If no unique data is passed as an argument, set app settings to reference the defaults
        else:
            data_keys = json_data.keys()
            for data_key in data_keys:
                key_path = list(json_file[1])
                key_path[0] = show

                key_path.append(str(data_key))
                key_path.append('$ref')

                full_ref = ref_string + data_key
                config.updateJson(key_path, full_ref, resolveRef=False)


class Environment(object):
    """
    # Environment

    Defines the main environment class that handles key variables like SHOW, SEQ, and SHOT.

    """

    def __init__(self):
        # Testing variables.
        self.SHOW = 'HONU'
        self.SEQ = 'ABC'
        self.SHOT = '010'

    def setShow(self, show):
        """
        Sets show variable.

        :param show: String of show name.
        :return: 0 for success, 1 for failure.
        """
        if show:
            self.SHOW = str(show)
            return 0
        return 1

    def setSeq(self, seq):
        """
        Sets sequence variable.

        :param seq: String of sequence name.
        :return: 0 for success, 1 for failure.
        """
        if seq:
            self.SEQ = str(seq)
            return 0
        return 1

    def setShot(self, shot):
        """
        Sets shot variable.

        :param shot: String of shot variable.
        :return: 0 for success, 1 for failure
        """
        if shot:
            self.SEQ = str(shot)
            return 0
        return 1

    def os(self):
        """
        Returns the current operating system.

        :return: String defining the current operating system.
        """
        curos = platform.system()
        return curos.lower()

    def rootlocal(self, path=None):
        """
        Returns the root path for the local directory, containing individual show folders.
        Raises ValueError if the root directory doesn't exist.

        :param path: If path is specified, sets the local directory to path if it exists.
        :return: Path on success, None on failure.
        """
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'localdir', str(path))
                return path
            return None

        localdir = config.rootSettings()['paths']['local']
        if not os.path.isdir(localdir):
            raise ValueError, "[%s] Local Directory does not exist." % localdir
        return localdir

    def rootserver(self, path=None):
        """
        Returns the root path for the server directory, containing individual show folders.
        Raises ValueError if the root directory doesn't exist.

        :param path: If path is specified, sets the server directory to path if it exists.
        :return: Path on success, None on failure.
        """
        if path is not None:
            if os.path.isdir(path):
                config.setvalue('root', 'serverdir', str(path))
                return path
            return None

        serverdir = config.rootSettings()['paths']['server']
        if not  os.path.isdir(serverdir):
            raise ValueError, "[%s] Server Directory does not exist." % serverdir
        return serverdir

    def shotdirectory(self, rootindex=1, folderindex=1, show=None, seq=None, shot=None):
        """
        Returns directory for particular show/seq/shot combination.

        :param rootindex: Index defines what root path to ues, 1 for server, 0 for local.
        :param folderindex: Index of shot directory to use, 1 for working (shots), 0 for publish.
        :param show: Show used to build path.
        :param seq: Sequence used to build path.
        :param shot: Shot used to build path.
        :return: Path on success, 1 on failure.
        """

        basepaths = [self.rootlocal(), self.rootserver()]
        subpaths = ['publish', 'shots']

        root_path = os.path.join(basepaths[rootindex], show)
        sub_path = os.path.join(root_path, "_production", subpaths[folderindex])

        if show is not None:
            if seq is not None:
                if shot is not None:
                    path = os.path.join(sub_path, seq, shot)
                    if not os.path.isdir(path):
                        print 'Path [%s] does not exist' % path
                        return 1
                    return path

                path = os.path.join(sub_path, seq)
                if not os.path.isdir(path):
                    print 'Path [%s] does not exist' % path
                    return 1
                return path

            path = root_path
            if not os.path.isdir(path):
                print 'Path [%s] does not exist' % path
                return 1
            return path

        path = basepaths[rootindex]

        if not os.path.isdir(path):
            print "Path [%s] does not exist" % path
            return 1
        return path

    def envstr(self, var):
        """
        Not sure what this is doing anymore... Probably need to remove.
        :param var:
        :return:
        """
        key = '%s' % str(var).upper()
        return key

    def getenv(self, var):
        """
        Returns environment variable value.

        :param var: Environment variable key.
        :return: Env variable value on success, ValueError on failure.
        """
        key = self.envstr(var)
        envvar = os.getenv(key)
        if not envvar:
            raise ValueError, "[%s] Environment Variable does not exist" % key
        return envvar

    def currentUser(self):
        """
        Return current username.
        :return: Current user name.
        """
        return getpass.getuser()

    def runningprocess(self):
        """
        Prints running processes of supported applications (defined in configuration.json)
        :return: None
        """
        for a in self.supportedapps():
            value = config.applicationSettings(str(a), self.SHOW)[self.os()]
            for p in psutil.process_iter():
                try:
                    if p.exe() == value:
                        print '%s [%s] @ %s' % (p.name(), p.pid, p.create_time())
                # It's going to lock the user out of most process
                except psutil.Error:
                    pass

    def supportedapps(self):
        """
        Returns the currently supported applications (as defined in configuation.json).
        :return: List of application names.
        """
        apps = config.supportedApplications(self.SHOW)
        return apps

    def allShows(self):
        """
        Returns all shows (as defined in configuration.json).
        :return: List of show names.
        """
        shows = config.readJson().keys()
        return shows

    def sequences(self):
        """
        Returns all sequences defined for the current show.
        :return: List of sequence names.
        """
        seqs = sorted(config.sequences(self.SHOW))
        return seqs

    def shots(self, seq):
        """
        Returns all shots defined for the current show / sequence combination.
        :param seq: Sequence to return shots for.
        :return: List of shots for show/seq combo.
        """
        shots = sorted(config.shots(self.SHOW, seq))
        return shots

    def addShot(self, seq, shot):
        """
        Creates a shot, adding it to the configuration.conf file.
        :param seq: Sequence to create (if it already exists, the shot will be added to the existing seq)
        :param shot: Shot name to create.
        :return: None
        """
        key_path = ['definitions', 'sequences', str(seq).lower(), str(shot).lower(), "$ref"]
        value = '#/definitions/shotfolders'
        json_filename = 'folders.%s.json' % str(self.SHOW).lower()
        config.updateJson(key_path, value, filename=json_filename, resolveRef=False)

    def applicationSettings(self, app):
        """
        Returns dictionary of settings for a particular application.
        :param app: Application for which to return settings.
        :return: Dict of settings.
        """
        settings = config.applicationSettings(app, show=self.SHOW)
        return settings

    def stages(self):
        """
        Returns stage data for the stages defined in the show specific file (stages.SHOW.json)
        :return: Return sorted list (by id of stage) of stage data.
        """
        stage_str = 'stages.%s.json' % self.SHOW

        json_data = config.readJson(stage_str)
        stage_list = sorted(json_data.values(), key=itemgetter('id'))

        return stage_list


class Application(object):
    """
    Base application class that defines variables and methods for launching files and handling file metadata.
    """

    def __init__(self, env, app, uid):
        """
        Setup variables for the application class.

        :param env: Requires the common environment be passed in for access to SHOW/SEQ/SHOT
        :param app: Defines what application will be launched, thus what files will be searched for.
        :param uid: Base unique id for the application.
        """
        self.environment = env
        self.app = app

        self.file = None
        self.fileExists = False

        self.project = None
        self.script = None
        self.version = None

        self.arguments = {}

        self.path = config.applicationSettings(self.app, self.environment.SHOW)[self.environment.os()]
        self.pathExists = False
        if os.path.isfile(self.path):
            self.pathExists = True

        self.id = uid
        self.rids = []

    def setpath(self, path=None):
        """
        Set executable file? Yeah, this method isn't used...
        :param path:
        :return:
        """
        if path is not None and os.path.isfile(path):
            self.path = path
            self.pathExists = True
            # config.setvalue(self.app.lower(), 'mac', self.path)

    def setfile(self, file=None):
        """
        Sets the file that will be launched.

        :param file: File path of the currently ready-to-launch file.
        :return: file path of the currently set file.
        """
        if file is not None and os.path.isfile(file):
            self.file = file
            self.fileExists = True
            return file
        else:
            print('NO FILE SIR')
            return None

    def getFile(self, stage='', tag=''):
        """
        Returns the latest file for the SHOW/SEQ/SHOT combo, with optional filter options.

        :param stage: (Optional) Stage string to filter search to files that contain this string.
        :param tag: (Optional) Tag string to filter search to files that contain this tag.
        :return: Most recently modified file that fits all filters.
        """
        base_directory = self.environment.shotdirectory(show=self.environment.SHOW,
                                                        seq=self.environment.SEQ,
                                                        shot=self.environment.SHOT)

        latestFiles = []

        for file_type in self.fileTypes():
            tag_string = tag
            stage_string = stage

            if tag is not '':
                tag_string = '_%s' % tag
            if stage is not '':
                stage_string = '_st%s' % stage

            searchString = '*%s%s_*%s' % (stage_string, tag_string, file_type)
            searchPath = os.path.join(base_directory, self.app)
            if self.app == 'maya':
                searchPath = os.path.join(searchPath, 'scenes')
            searchPath = os.path.join(searchPath, searchString)

            files = list(glob.iglob(searchPath))
            if files:
                latest = max(files, key=os.path.getmtime)
                latestFiles.append(latest)

        if latestFiles:
            latest = max(latestFiles, key=os.path.getmtime)
            print latest
            self.file = latest
            return latest
        return None

    def getFileDate(self, file_path):
        """
        Returns the modify datetime of the passed in file.
        :param file_path: Eile path of file to check datetime for.
        :return: Float definition of mtime.
        """
        if platform.system() == 'Windows':
            return os.path.getmtime(file_path)
        else:
            stat = os.stat(file_path)
            try:
                return stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                return stat.st_mtime

    def tags(self, stage):
        """
        Returns a list of unique tags that exist for the current stage.

        :param stage: Current stage to check tags for.
        :return:
        """
        all_files = []
        tags = []
        base_directory = self.environment.shotdirectory(show=self.environment.SHOW,
                                                        seq=self.environment.SEQ,
                                                        shot=self.environment.SHOT)
        for file_type in self.fileTypes():
            stage_str = '_st%s' % stage
            search_str = '*%s*%s' % (stage_str, file_type)

            search_path = os.path.join(base_directory, self.app)
            if self.app == 'maya':
                search_path = os.path.join(search_path, 'scenes')
            search_path = os.path.join(search_path, search_str)

            files = list(glob.iglob(search_path))
            all_files += files

        for index, file_path in enumerate(all_files):
            filename = os.path.basename(file_path)
            name_parts = filename.split('_')
            if len(name_parts) > 4:
                tags.append(name_parts[3])

        distict_tags = set(tags)
        return distict_tags

    def setversion(self, version=None):
        """
        Probably don't need this method either..
        :param version:
        :return:
        """
        if version is not None:
            self.version = version
            config.setvalue(self.app.lower(), 'version', self.version)

    def instances(self):
        """
        Finds all currently running instances of the current application.
        :return: None
        """
        for p in psutil.process_iter():
            try:
                if p.exe() == self.path:
                    env = p.environ()
                    if env.has_key('HASH'):
                        cid = env['HASH']
                        self.rids.append(int(cid))

                        seq_str = self.environment.envstr('SEQ')
                        shot_str = self.environment.envstr('SHOT')

                        print '%s [PID %s] %s %s:%s' % (p.name(), p.pid, cid, env[seq_str], env[shot_str])
                    else:
                        print '%s [PID %s] Was not assigned a hash' % (p.name(), p.pid)
            # It's going to lock the user out of most process
            except psutil.Error:
                pass

    def run(self):
        """
        Runs the set file using the application path for the correct operating system.
        :return: None
        """
        sid = self.id
        if sid not in self.rids:
            self.rids.append(sid)
        else:
            maxid = max(self.rids)
            sid = maxid + 1
            self.rids.append(sid)

        cenv = os.environ.copy()
        cenv['HASH'] = str(sid)

        show_str = self.environment.envstr('SHOW')
        cenv[show_str] = str(self.environment.SHOW)

        seq_str = self.environment.envstr('SEQ')
        cenv[seq_str] = str(self.environment.SEQ)

        shot_str = self.environment.envstr('SHOT')
        cenv[shot_str] = str(self.environment.SHOT)

        args = self.args()
        if args:
            subprocess.Popen(args, env=cenv)

    def version(self):
        """
        Returns the current version of the application.
        :return: Current version.
        """
        if self.version is None:
            ver = config.applicationSettings(self.app, self.environment.SHOW)['version']
            if ver:
                self.version = ver
                return ver
        return self.version

    def args(self):
        """
        Builds the argument set for the current application. A bit hardcoded at the moment, want to move this out into the configuation files.
        :return: List of arguments.
        """

        self.arguments = {
            'maya': {'-file': self.file,
                     '-proj': self.project,
                     '-script': self.script},
            'nuke': {'--nukex': True,
                     '-b': True,
                     '--': self.file},
            'houdini': {'-n': self.file}
        }

        args = []

        if self.app is not None:
            if self.app.lower() in self.arguments:
                for key, value in self.arguments[self.app.lower()].iteritems():
                    if value is not None and value is not False:
                        args.append(key)

                        # Don't want to append the True value (has to be true to get this far)
                        # Want to retain the ability to turn singular flags on and off
                        if value is True:
                            continue

                        args.append(value)

        return [self.path] + args

    def fileTypes(self):
        """
        Returns the file types for the current application.
        :return: list of extensions.
        """
        if self.app:
            file_types = config.applicationSettings(self.app, self.environment.SHOW)['filetypes']
            if file_types:
                return file_types
            return 1
        return 1


if __name__ == "__main__":
    environment = Environment()
    setup = Setup(environment)
    setup.createBaseStructure()
