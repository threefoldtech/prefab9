from js9 import j

base = j.tools.prefab._getBaseClass()


class PrefabCockpit(base):

    def install(self, start=True, branch="8.2.0", reset=False, ip="localhost", production=False,
                client_id='', ays_secret='', portal_secret='', organization=''):
        """
        This will install the all the component of the cockpit in one command.
        (mongodb, portal, atyourservice)

        production: cockpit mode (atyourservice and portal in development mode if False)

        client_id: oauth client id
        ays_secret: client secret of ays
        portal_secret: client secret of portal
        organization: oauth organization

        Make sure that you don't have uncommitted code in any code repository cause this method will discard them !!!
        """
        self.install_deps()
        # install mongodb, required for portal
        self.prefab.apps.mongodb.install(start=start, reset=reset)

        # install portal
        self.prefab.apps.portal.install(start=False, branch=branch, reset=reset)
        # add link from portal to API
        # 1- copy the nav to the portalbase and then edit it
        content = self.prefab.core.file_read(
            '$CODEDIR/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81/.space/nav.wiki')

        # 2- fix the ays api endpoint.
        content = content.replace('AYS API:http://localhost:5000', "AYS API:http://{ip}:5000".format(ip=ip))
        self.prefab.core.file_write('$JSAPPSDIR/portals/main/base/AYS81/.space/nav.wiki', content=content)

        self.prefab.apps.portal.stop()
        self.prefab.apps.portal.configure(
            production=production,
            client_id=client_id,
            client_secret=portal_secret,
            organization=organization,
            redirect_address='%s:8200' %
            ip)

        self.prefab.apps.atyourservice.install()
        self.prefab.apps.atyourservice.stop()
        self.prefab.apps.atyourservice.configure(
            production=production,
            client_secret=ays_secret,
            client_id=client_id,
            organization=organization,
            redirect_address='%s:8200' %
            ip)

        # configure base URI for api-console
        raml = self.prefab.core.file_read('$JSAPPSDIR/atyourservice/apidocs/api.raml')
        raml = raml.replace('baseUri: http://localhost:5000', "baseUri: http://{ip}:5000".format(ip=ip))
        self.prefab.core.file_write('$JSAPPSDIR/atyourservice/apidocs/api.raml', raml)

        if start:
            # start API and daemon
            self.start(host=ip)

    def start(self, host='localhost'):
        # start AYS server
        # start portal
        self.prefab.apps.atyourservice.start(host=host)
        self.prefab.apps.portal.start()

    def stop(self):
        self.prefab.apps.atyourservice.stop()
        self.prefab.apps.portal.stop()

    def install_deps(self):
        self.prefab.package.mdupdate()
        self.prefab.package.install('libssl-dev')

        deps = """
        cryptography
        python-jose
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self.prefab.development.pip.multiInstall(deps, upgrade=True)