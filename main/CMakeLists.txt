# ==============================================================================
# main/CMakeLists.txt — ESP-IDF Component Registration
# ==============================================================================


idf_component_register(
    SRCS "root32.c"
    REQUIRES driver freertos
)
