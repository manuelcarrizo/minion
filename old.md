### Status
Here you can see all the services running, versions installed and start/stop/restart services.
Information is obtained using Spring Boot `health` and `info` endpoints.
![Status](images/status.png)

### Releases
Here you can see the `releases` versions on Sonatype Nexus per artifact and start a deploy.
![Releases](images/releases.png)

### Snapshots
Here you can see the `snapshots` versions on Sonatype Nexus per artifact and start a deploy.
![Snapshots](images/snapshots.png)

### Build
This tab lets you see all the branches on the projects and schedule a build on Jenkins, after the build is done the artifact is automatically deployed on this minion.
![Build](images/build.png)

### Properties
Edit a configuration file per service, lets you create a copy of the current configuration and restore that copy later.
![Properties](images/properties.png)

### Log
See the log files of each service, the user can activate autoreloading or reload manually.
![Log](images/log.png)
