from conans import ConanFile, CMake, tools
from pathlib import Path
import os, shutil


class OsgearthConan(ConanFile):
    name = "osgearth"
    version = "2.10.1"
    license = "LGPL-3"
    settings = "os", "compiler", "build_type", "arch"
    options = {
	    "shared": [True, False],
	    "fPIC": [True, False],
        "geos": [True, False]
	}
    default_options = {
        "shared": True,
        "fPIC": True,
        "geos": True
    }
    build_requires = "cmake_installer/3.15.4@conan/stable"
    requires = (
        "openscenegraph/3.6.4@bincrafters/stable",
        "libcurl/7.61.1@bincrafters/stable",
		"protobuf/3.6.1@bincrafters/stable",
		"Poco/1.7.9@pocoproject/stable",
        "gdal/2.4.2@insanefactory/stable"
    )
    generators = "cmake"
    exports_sources = "FindOSG.cmake"
    download_prefix = "https://github.com/gwaldron/osgearth/archive"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11@conan/stable", override=True)
        self.requires("libjpeg/9c@bincrafters/stable", override=True)
        self.requires("libpng/1.6.37@bincrafters/stable", override=True)
        self.requires("libtiff/4.0.9@bincrafters/stable", override=True)
        self.requires("OpenSSL/1.0.2o@conan/stable", override=True)
        self.requires("bzip2/1.0.8@conan/stable", override=True)
        self.requires("freetype/2.10.0@bincrafters/stable", override=True)
        self.requires("sqlite3/3.29.0@bincrafters/stable", override=True)

        if self.options.geos:
            self.requires("geos/3.7.3@insanefactory/stable")

    def source(self):
        name = "osgearth"
        tools.get("{0}/{1}-{2}.tar.gz".format(self.download_prefix, name, self.version))
        extracted_dir = "{0}-{0}-".format(name) + self.version
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "PROJECT(OSGEARTH)",
            '''PROJECT(OSGEARTH)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
link_directories(${CONAN_LIB_DIRS})'''
        )

        os.remove(os.path.join(self._source_subfolder, "CMakeModules", "FindOSG.cmake"))
        shutil.move("FindOSG.cmake", os.path.join(self._source_subfolder, "CMakeModules"))

    def build(self):
        osgDir = str(Path(self.deps_cpp_info["openscenegraph"].include_paths[0]).parent)
        gdalDir = str(Path(self.deps_cpp_info["gdal"].include_paths[0]).parent)

        cmake = CMake(self)
        
        cmake.definitions["DYNAMIC_OSGEARTH"] = self.options.shared
        cmake.definitions["PROTOBUF_USE_DLLS"] = self.options["protobuf"].shared

        cmake.definitions["BUILD_OSGEARTH_EXAMPLES"] = False
        cmake.definitions["BUILD_APPLICATIONS"] = False
        cmake.definitions["BUILD_TESTS"] = False
        
        cmake.definitions["CURL_INCLUDE_DIR"] = self.deps_cpp_info["libcurl"].include_paths[0]
        cmake.definitions["CURL_LIBRARY"] = self.deps_cpp_info["libcurl"].libs[0]
        cmake.definitions["OSG_DIR"] = osgDir
        cmake.definitions["GDAL_DIR"] = gdalDir

        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        if os.path.exists(os.path.join(self.package_folder, "lib64")):
            os.rename(os.path.join(self.package_folder, "lib64"), os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

