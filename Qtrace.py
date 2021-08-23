import re
import pandas
import pandas as pd
def file_reader(f_name) -> pandas.core.frame.DataFrame:
    pattern = re.compile(r'\d+')
    pattern_iters = re.compile(r'ANALYSIS')
    pattern_DL_extras = \
        re.compile(r'\| NR \|.*?PHY.*?\d{0,7}.*?MAC.*?\d{0,7}.*?RLC.*?\d{0,7}.*?PDCP.*?\d{0,7}.*?IPA.*?\d+')
    pattern_UL_extras = re.compile(r'\| NR \|.*?IPA.*?\d{0,6}.*?L2UL.*?\d{0,6}.*?PHY.*?\d+')
    pattern_cc0_DL = re.compile(r'NR5GMAC.*?DL.*?0.*?[aA]vgPHY.*?: \d+')
    pattern_cc1_DL = re.compile(r'NR5GMAC.*?DL.*?1.*?[aA]vgPHY.*?: \d+')
    pattern_cc2_DL = re.compile(r'NR5GMAC.*?DL.*?2.*?[aA]vgPHY.*?: \d+')
    pattern_cc3_DL = re.compile(r'NR5GMAC.*?DL.*?3.*?[aA]vgPHY.*?: \d+')
    pattern_cc4_DL = re.compile(r'NR5GMAC.*?DL.*?4.*?[aA]vgPHY.*?: \d+')
    pattern_cc5_DL = re.compile(r'NR5GMAC.*?DL.*?5.*?[aA]vgPHY.*?: \d+')
    pattern_cc6_DL = re.compile(r'NR5GMAC.*?DL.*?6.*?[aA]vgPHY.*?: \d+')
    pattern_cc7_DL = re.compile(r'NR5GMAC.*?DL.*?7.*?[aA]vgPHY.*?: \d+')
    pattern_cc0_UL = re.compile(r'NR5GMAC.*?UL.*?0.*?[aA]vgPHY.*?: \d+')
    pattern_cc1_UL = re.compile(r'NR5GMAC.*?UL.*?1.*?[aA]vgPHY.*?: \d+')
    # matches = pattern.finditer()
    text = ""
    file_contents = "\n"
    aggregate_tput = 0
    list = ""
    aggregate_PHY = 0
    aggregate_MAC = 0
    aggregate_RLC = 0
    aggregate_PDCP = 0
    aggregate_IPA = 0
    aggregate_IPA_UL = 0
    aggregate_L2UL = 0
    aggregate_PHY_UL = 0
    aggregate_cc0_DL_tput = 0
    aggregate_cc1_DL_tput = 0
    aggregate_cc2_DL_tput = 0
    aggregate_cc3_DL_tput = 0
    aggregate_cc4_DL_tput = 0
    aggregate_cc5_DL_tput = 0
    aggregate_cc6_DL_tput = 0
    aggregate_cc7_DL_tput = 0
    aggregate_cc0_UL_tput = 0
    aggregate_cc1_UL_tput = 0
    cells = 0
    cell_tput = 0
    total_iterations = 0
    i = 0
    carrier_change_DL = 0
    carrier_change_UL = 0
    UL_cc0 = 0
    UL_cc1 = 0
    DL_cc0 = 0
    DL_cc1 = 0
    DL_cc2 = 0
    DL_cc3 = 0
    DL_cc4 = 0
    DL_cc5 = 0
    DL_cc6 = 0
    DL_cc7 = 0
    # what type of excel sheet the file is
    # 0 - SDx60
    # 1 - SDx55
    excel_type = 0
    with open(f_name) as f:
        file_contents = f.read()
        # print(pattern)
        matches_iters = pattern_iters.findall(file_contents)
        matches_DL_extras = pattern_DL_extras.findall(file_contents)
        matches_UL_extras = pattern_UL_extras.findall(file_contents)
        matches_cc0_DL = pattern_cc0_DL.findall(file_contents)
        matches_cc1_DL = pattern_cc1_DL.findall(file_contents)
        matches_cc2_DL = pattern_cc2_DL.findall(file_contents)
        matches_cc3_DL = pattern_cc3_DL.findall(file_contents)
        matches_cc4_DL = pattern_cc4_DL.findall(file_contents)
        matches_cc5_DL = pattern_cc5_DL.findall(file_contents)
        matches_cc6_DL = pattern_cc6_DL.findall(file_contents)
        matches_cc7_DL = pattern_cc7_DL.findall(file_contents)
        matches_cc0_UL = pattern_cc0_UL.findall(file_contents)
        matches_cc1_UL = pattern_cc1_UL.findall(file_contents)
        for match in matches_iters:
            total_iterations += 1
        for match in matches_DL_extras:
            list = match.split(" ")
            if (list[4] == 'since'):
                excel_type = 1
                PHY_value = list[7]
                aggregate_PHY += int(PHY_value)
                MAC_value = list[10]
                aggregate_MAC += int(MAC_value)
                RLC_value = list[16]
                aggregate_RLC += int(RLC_value)
                PDCP_value = list[19]
                aggregate_PDCP += int(PDCP_value)
                IPA_value = list[22]
                aggregate_IPA += int(IPA_value)
            elif (list[3] == 'tput.kbps:[PHY:'):
                PHY_value = list[4]
                PHY_value = PHY_value[:-1]
                aggregate_PHY += int(PHY_value)
                MAC_value = list[6]
                MAC_value = MAC_value[:-1]
                aggregate_MAC += int(MAC_value)
                RLC_value = list[10]
                RLC_value = RLC_value[:-1]
                aggregate_RLC += int(RLC_value)
                PDCP_value = list[12]
                PDCP_value = PDCP_value[:-1]
                aggregate_PDCP += int(PDCP_value)
                IPA_value = list[14]
                IPA_value = IPA_value[:-1]
                aggregate_IPA += int(IPA_value)
        for match in matches_UL_extras:
            list = match.split(" ")
            if (list[4] == 'since'):
                IPA_UL_value = list[7]
                aggregate_IPA_UL += int(IPA_UL_value)
                L2UL_value = list[13]
                aggregate_L2UL += int(L2UL_value)
                PHY_UL_value = list[19]
                aggregate_PHY_UL += int(PHY_UL_value)
            elif (list[3] == 'tput.kbps:[IPA:'):
                IPA_UL_value = list[4]
                IPA_UL_value = IPA_UL_value[:-1]
                aggregate_IPA_UL += int(IPA_UL_value)
                L2UL_value = list[8]
                L2UL_value = L2UL_value[:-1]
                aggregate_L2UL += int(L2UL_value)
                PHY_UL_value = list[12]
                aggregate_PHY_UL += int(PHY_UL_value)
        for match in matches_cc0_DL:
            DL_cc0 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc0_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc0_DL_tput += tput
        for match in matches_cc1_DL:
            DL_cc1 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc1_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc1_DL_tput += tput
        for match in matches_cc2_DL:
            DL_cc2 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc2_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc2_DL_tput += tput
        for match in matches_cc3_DL:
            DL_cc3 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc3_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc3_DL_tput += tput
        for match in matches_cc4_DL:
            DL_cc4 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc4_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc4_DL_tput += tput
        for match in matches_cc5_DL:
            DL_cc5 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc5_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc5_DL_tput += tput
        for match in matches_cc6_DL:
            DL_cc6 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc6_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc6_DL_tput += tput
        for match in matches_cc7_DL:
            DL_cc7 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc7_DL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc7_DL_tput += tput
        for match in matches_cc0_UL:
            UL_cc0 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc0_UL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc0_UL_tput += tput
        for match in matches_cc1_UL:
            UL_cc1 += 1
            if (excel_type):
                list = match[39:]
                matches = pattern.findall(list)
                tput = int(matches[0])
                aggregate_cc1_UL_tput += tput
            elif (excel_type == 0):
                list = match[39:]
                tput = int(list)
                aggregate_cc1_UL_tput += tput
    f.close()
    if (UL_cc0 > 0 and UL_cc0 != total_iterations):
        carrier_change_UL = 1
    if (UL_cc1 > 0 and UL_cc1 != total_iterations):
        carrier_change_UL = 1
    if (carrier_change_UL):
        print("# of UL carriers changed")
    if (DL_cc0 > 0 and DL_cc0 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc1 > 0 and DL_cc1 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc2 > 0 and DL_cc2 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc3 > 0 and DL_cc3 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc4 > 0 and DL_cc4 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc5 > 0 and DL_cc5 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc6 > 0 and DL_cc6 != total_iterations):
        carrier_change_DL = 1
    if (DL_cc7 > 0 and DL_cc7 != total_iterations):
        carrier_change_DL = 1
    if (carrier_change_DL):
        print("# of DL carriers changed")
    PHY_DL = int(aggregate_PHY / total_iterations)
    MAC = int(aggregate_MAC / total_iterations)
    RLC = int(aggregate_RLC / total_iterations)
    PDCP = int(aggregate_PDCP / total_iterations)
    IPA_DL = int(aggregate_IPA / total_iterations)
    IPA_UL = int(aggregate_IPA_UL / total_iterations)
    L2UL = int(aggregate_L2UL / total_iterations)
    PHY_UL = int(aggregate_PHY_UL / total_iterations)
    cc0_DL = int(aggregate_cc0_DL_tput / total_iterations)
    cc1_DL = int(aggregate_cc1_DL_tput / total_iterations)
    cc2_DL = int(aggregate_cc2_DL_tput / total_iterations)
    cc3_DL = int(aggregate_cc3_DL_tput / total_iterations)
    cc4_DL = int(aggregate_cc4_DL_tput / total_iterations)
    cc5_DL = int(aggregate_cc5_DL_tput / total_iterations)
    cc6_DL = int(aggregate_cc6_DL_tput / total_iterations)
    cc7_DL = int(aggregate_cc7_DL_tput / total_iterations)
    cc0_UL = int(aggregate_cc0_UL_tput / total_iterations)
    cc1_UL = int(aggregate_cc1_UL_tput / total_iterations)
    # print("Average PHY value for DL = ", int(aggregate_PHY / total_iterations), "Kbps")
    # print("Average MAC value = ", int(aggregate_MAC / total_iterations))
    # print("Average RLC value = ", int(aggregate_RLC / total_iterations))
    # print("Average PDCP value = ", int(aggregate_PDCP / total_iterations))
    # print("Average IPA value for DL = ", int(aggregate_IPA / total_iterations))
    # print("Average IPA value for UL = ", int(aggregate_IPA_UL / total_iterations))
    # print("Average L2UL value = ", int(aggregate_L2UL / total_iterations))
    # print("Average PHY value for UL = ", int(aggregate_PHY_UL / total_iterations), "Kbps")
    # print("Average Tput for cc0 for DL = ", int(aggregate_cc0_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc1 for DL = ", int(aggregate_cc1_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc2 for DL = ", int(aggregate_cc2_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc3 for DL = ", int(aggregate_cc3_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc4 for DL = ", int(aggregate_cc4_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc5 for DL = ", int(aggregate_cc5_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc6 for DL = ", int(aggregate_cc6_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc7 for DL = ", int(aggregate_cc7_DL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc0 for UL = ", int(aggregate_cc0_UL_tput / total_iterations), " Kbps")
    # print("Average Tput for cc1 for UL = ", int(aggregate_cc1_UL_tput / total_iterations), " Kbps")
    df = pd.DataFrame()
    # df['Measurement'] = ['PHY(DL)', 'MAC', 'RLC', 'PDCP', 'IPA(DL)', 'IPA(UL)', 'L2UL', 'PHY(UL)',
    #                      'CC0(DL)', 'CC1(DL)', 'CC2(DL)', 'CC3(DL)', 'CC4(DL)', 'CC5(DL)', 'CC6(DL)', 'CC7(DL)',
    #                      'CC0(UL)', 'CC1(UL)']
    # df['Value'] = [PHY_DL, MAC, RLC, PDCP, IPA_DL, IPA_UL, L2UL, PHY_UL, cc0_DL, cc1_DL, cc2_DL, cc3_DL, cc4_DL,
    #                cc5_DL, cc6_DL, cc7_DL, cc0_UL, cc1_UL]
    df['PHY(DL)'] = [PHY_DL]
    df['MAC'] = [MAC]
    df['RLC'] = [RLC]
    df['PDCP'] = [PDCP]
    df['IPA(DL)'] = [IPA_DL]
    df['IPA(UL)'] = [IPA_UL]
    df['L2UL'] = [L2UL]
    df['PHY(UL)'] = [PHY_UL]
    df['CC0_DL'] = [cc0_DL]
    df['CC1_DL'] = [cc1_DL]
    df['CC2_DL'] = [cc2_DL]
    df['CC3_DL'] = [cc3_DL]
    df['CC4_DL'] = [cc4_DL]
    df['CC5_DL'] = [cc5_DL]
    df['CC6_DL'] = [cc6_DL]
    df['CC7_DL'] = [cc7_DL]
    df['CC0_UL'] = [cc0_UL]
    df['CC1_UL'] = [cc1_UL]
    # df.to_csv('')
    # print(df)
    return df