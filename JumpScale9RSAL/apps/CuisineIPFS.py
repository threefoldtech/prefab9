from js9 import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineIPFS(app):
    NAME = "ipfs"

    def isInstalled(self):
        """
        Checks if a package is installed or not
        You can ovveride it to use another way for checking
        """
        return self.cuisine.core.file_exists('$BINDIR/ipfs')

    def install(self, name='main', reset=False):
        if reset is False and self.isInstalled():
            return

        if self.cuisine.platformtype.isLinux:
            url = "https://dist.ipfs.io/go-ipfs/v0.4.4/go-ipfs_v0.4.4_linux-amd64.tar.gz"
        elif "darwin" in self.cuisine.platformtype.osname:
            url = "https://dist.ipfs.io/go-ipfs/v0.4.4/go-ipfs_v0.4.4_darwin-amd64.tar.gz"

        name = url.split('/')[-1]
        compress_path = self.replace('$TMPDIR/{}'.format(name))
        self.cuisine.core.file_download(url, compress_path)

        uncompress_path = self.replace('$TMPDIR/go-ipfs')
        if self.cuisine.core.file_exists(uncompress_path):
            self.cuisine.core.dir_remove(uncompress_path)

        self.cuisine.core.run("cd $TMPDIR; tar xvf {}".format(name))
        self.cuisine.core.file_copy('{}/ipfs'.format(uncompress_path), '$BINDIR/ipfs')

    def uninstall(self):
        """
        remove ipfs binary from $BINDIR
        """
        if self.cuisine.core.file_exists('$BINDIR/ipfs'):
            self.cuisine.core.file_unlink('$BINDIR/ipfs')

    def start(self, name='main', readonly=False):
        cfg_dir = '$JSCFGDIR/ipfs/{}'.format(name)
        if not self.cuisine.core.file_exists(cfg_dir):
            self.cuisine.core.dir_ensure(cfg_dir)

        # check if the ipfs repo has not been created yet.
        if not self.cuisine.core.file_exists(cfg_dir + '/config'):
            cmd = 'IPFS_PATH={} $BINDIR/ipfs init'.format(cfg_dir)
            self.cuisine.core.run(cmd)

        cmd = '$BINDIR/ipfs daemon'
        if not readonly:
            cmd += '  --writable'

        self.cuisine.processmanager.ensure(
            name='ipfs_{}'.format(name),
            cmd=cmd,
            path=cfg_dir,
            env={'IPFS_PATH': cfg_dir}
        )

    def stop(self, name='main'):
        self.cuisine.processmanager.stop(name='ipfs_{}'.format(name))
