# Numeric python library build that is dependent on compiler toolchain

#-fsp-header-comp-begin----------------------------------------------

%include %{_sourcedir}/FSP_macros

# FSP convention: the default assumes the gnu compiler family;
# however, this can be overridden by specifing the compiler_family
# variable via rpmbuild or other mechanisms.

%{!?compiler_family: %define compiler_family gnu}
%{!?PROJ_DELIM:      %define PROJ_DELIM   %{nil}}

# Compiler dependencies
BuildRequires: lmod%{PROJ_DELIM}
%if %{compiler_family} == gnu
BuildRequires: gnu-compilers%{PROJ_DELIM}
Requires:      gnu-compilers%{PROJ_DELIM}
%endif
%if %{compiler_family} == intel
BuildRequires: gcc-c++ intel-compilers%{PROJ_DELIM}
Requires:      gcc-c++ intel-compilers%{PROJ_DELIM}
%if 0%{FSP_BUILD}
BuildRequires: intel_licenses
%endif
%endif

#-fsp-header-comp-end------------------------------------------------

# Base package name
%define pname numpy
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])

Name:      python-%{pname}-%{compiler_family}%{PROJ_DELIM}
Version:   1.9.1
Release:   1
Summary:   NumPy array processing for numbers, strings, records and objects
URL:       http://sourceforge.net/projects/numpy
License:   BSD-3-Clause
Group:     Development/Libraries/Python
Source0:   %{pname}-%{version}.tar.gz
Source1:   FSP_macros
Source2:   FSP_setup_compiler
Patch1:    numpy-buildfix.patch
BuildRoot: %{_tmppath}/%{pname}-%{version}-%{release}-root
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  python-devel
Requires:       python >= %{py_ver}
Provides:       numpy = %{version}
%if 0%{?suse_version}
BuildRequires:  fdupes
#!BuildIgnore: post-build-checks
%endif
%if ! 0%{?fedora_version}
Provides:       python-numeric = %{version}
Obsoletes:      python-numeric < %{version}
%endif

%define debug_package %{nil}

# Default library install path
%define install_path %{FSP_LIBS}/%{compiler_family}/%{pname}/%version

%description

NumPy is a general-purpose array-processing package designed to
efficiently manipulate large multi-dimensional arrays of arbitrary
records without sacrificing too much speed for small multi-dimensional
arrays.  NumPy is built on the Numeric code base and adds features
introduced by numarray as well as an extended C-API and the ability to
create arrays of arbitrary type which also makes NumPy suitable for
interfacing with general-purpose data-base applications. There are also 
basic facilities for discrete fourier transform, basic linear algebra,
and random number generation.

%prep
%setup -q -n %{pname}-%{version}
%patch1 -p1

%if %{compiler_family} == intel
export FSP_COMPILER_FAMILY=%{compiler_family}
. %{_sourcedir}/FSP_setup_compiler

cat > site.cfg << EOF
[mkl]
library_dirs = $MKLROOT/lib/intel64
include_dirs = $MKLROOT/include
mkl_libs = mkl_rt
lapack_libs =
EOF
%endif

%build
# FSP compiler/mpi designation
export FSP_COMPILER_FAMILY=%{compiler_family}
. %{_sourcedir}/FSP_setup_compiler

%if %{compiler_family} == intel
LDSHARED="icc -shared" \
%endif
CFLAGS="%{optflags} -fno-strict-aliasing" python setup.py build

%install
# FSP compiler designation
export FSP_COMPILER_FAMILY=%{compiler_family}
. %{_sourcedir}/FSP_setup_compiler
%define install_path %{FSP_LIBS}/%{compiler_family}/%{pname}/%version

#python setup.py install --root="%{buildroot}" --prefix="%{install_path}"
python setup.py install --root="%{buildroot}" --prefix=%{FSP_LIBS}/%{compiler_family}/%{pname}/%version
rm -rf %{buildroot}%{python_sitearch}/%{pname}/{,core,distutils,f2py,fft,ma,matrixlib,oldnumeric,polynomial,random,testing}/tests # Don't package testsuite
%if 0%{?suse_version}
%fdupes -s %{buildroot}%{_prefix}
%endif


# FSP module file
%{__mkdir} -p %{buildroot}%{FSP_MODULEDEPS}/%{compiler_family}/%{pname}
%{__cat} << EOF > %{buildroot}/%{FSP_MODULEDEPS}/%{compiler_family}/%{pname}/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the %{PNAME} library built with the %{compiler_family} compiler toolchain."
puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{PNAME} built with %{compiler_family} toolchain"
module-whatis "Version: %{version}"
module-whatis "Category: python module"
module-whatis "Description: %{summary}"
module-whatis "%{url}"

set             version		    %{version}

prepend-path    PATH                %{install_path}/bin
prepend-path    PYTHONPATH          %{install_path}/lib64/python2.7/site-packages

setenv          %{PNAME}_DIR        %{install_path}

EOF

%{__cat} << EOF > %{buildroot}/%{FSP_MODULEDEPS}/%{compiler_family}/%{pname}/.version.%{version}
#%Module1.0#####################################################################
##
## version file for %{pname}-%{version}
##
set     ModulesVersion      "%{version}"
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{FSP_HOME}

%changelog
