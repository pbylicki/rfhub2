*** Variables ***
#LOCATORS
${main_page_prefix}                //*[@id="root"]/div/main/div[2]
${main_page_collection_number}     ${main_page_prefix}/div/div/div/h2
${main_page_table}                 ${main_page_prefix}/div/div/div/table/tbody/tr[1]/td[1]
${left_panel_list}                 //*[@id="root"]/div/div/div/ul
${single_class_lib}                //*[contains(text(),"SingleClassLib")]
${lib_with_init}                   //*[contains(text(),"LibWithInit")]
${lib_with_init_2_method_1}        //*[contains(text(),"Lib With Init 2 Method 1")]
${overview}                        //*[contains(text(),"Overview")]
${test_libdoc_file}                //a[contains(text(), "Test Libdoc File")]
${detail_view_library_title}       ${main_page_prefix}/div/div/div/h2[1]
${detail_view_library_version}     ${main_page_prefix}/div/div/div/div[1]
${detail_view_library_scope}       ${main_page_prefix}/div/div/div/div[2]
${detail_view_library_overview}    ${main_page_prefix}/div/div/div/div[4]/p
${detail_view_library_keywords}    ${main_page_prefix}/div/div/div/h2[2]
${single_class_lib_items}          ${left_panel_list}/div/div/div/div
${search_field}                    //*[@id="root"]/div/header/div/div/div[2]/input
${search_hits_number}              ${main_page_collection_number}
${search_result_table}             ${main_page_prefix}/div/div/div/table/tbody/tr
${hamburger}                       //*[@id="root"]/div/header/div/button/span[1]/svg/path

#VARIABLES
${FIXTURES_PATH}                   ${CURDIR}/../../fixtures
${INITIAL_FIXTURES}                ${FIXTURES_PATH}/initial/
${BACKUP_FIXTURES}                 ${FIXTURES_PATH}/initial_bkp/
${UPDATED_FIXTURES}                ${FIXTURES_PATH}/updated/
${STATISTICS_PATH}                 ${FIXTURES_PATH}/statistics
${SUBDIR_PATH}                     ${STATISTICS_PATH}/subdir