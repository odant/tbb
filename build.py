# Intel TBB Conan package
# Dmitriy Vetutnev, Odant, 2018


import platform, os
from copy import deepcopy
from conan.packager import ConanMultiPackager


# Common settings
username = "odant" if "CONAN_USERNAME" not in os.environ else None
# Windows settings
visual_versions = ["15"] if "CONAN_VISUAL_VERSIONS" not in os.environ else None
visual_runtimes = ["MD", "MDd"] if "CONAN_VISUAL_RUNTIMES" not in os.environ else None
dll_sign = False if "CONAN_DISABLE_DLL_SIGN" in os.environ else True
built_in_tests = True if "TBB_BUILT_IN_TESTS" in os.environ else False


def add_dll_sign(builds):
    result = []
    for settings, options, env_vars, build_requires, reference in builds:
        options = deepcopy(options)
        options["tbb:dll_sign"] = dll_sign
        result.append([settings, options, env_vars, build_requires, reference])
    return result


def filter_libcxx(builds):
    result = []
    for settings, options, env_vars, build_requires, reference in builds:
        if settings["compiler.libcxx"] == "libstdc++11":
            result.append([settings, options, env_vars, build_requires, reference])
    return result


def add_built_in_tests(builds):
    result = []
    for settings, options, env_vars, build_requires, reference in builds:
        options = deepcopy(options)
        options["tbb:built_in_tests"] = built_in_tests
        result.append([settings, options, env_vars, build_requires, reference])
    return result


if __name__ == "__main__":
    builder = ConanMultiPackager(
        username=username,
        visual_versions=visual_versions,
        visual_runtimes=visual_runtimes,
        exclude_vcvars_precommand=True
    )
    builder.add_common_builds(pure_c=False)
    # Adjusting build configurations
    builds = builder.items
    if platform.system() == "Windows":
        builds = add_dll_sign(builds)
        builds = add_built_in_tests(builds)
    if platform.system() == "Linux":
        builds = filter_libcxx(builds)
    # Replace build configurations
    builder.items = []
    for settings, options, env_vars, build_requires, _ in builds:
        builder.add(
            settings=settings,
            options=options,
            env_vars=env_vars,
            build_requires=build_requires
        )
    builder.run()
