cmake_minimum_required(VERSION 3.16)
project(vulnscope_risk_engine LANGUAGES CXX)

add_executable(vulnscope-risk-engine risk_engine.cpp)
target_compile_features(vulnscope-risk-engine PRIVATE cxx_std_17)
# Project version: VulnScope V1.5







