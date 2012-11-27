# ganglia-ps
============

A Python-based ganglia module to add information about user processes to the
information published by the gmond process.
Processes from accounts listed in /etc/passwd are considered system processes
and excluded from the published list of processes.

# To build an RPM

Copy rpmspec/ganglia_ps.spec into the SPECS directory of your rpm build environment.
Adjust paths usr/lib64/ganglia/python_modules and etc/ganglia/conf.d if ganglia is
set up to use different directories.
Create a tarball of this project and copy it to the SOURCES directory of your rpm
build environment. Adjust version numbers in the spec file and the name of the tarball.
Then build the RPM:

		cd <rpm build env> && rpmbuild -bb SPECS/ganglia_ps.spec

