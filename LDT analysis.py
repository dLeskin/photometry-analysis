# coding=Utf-8
# parse LTD file according to http://www.helios32.com/Eulumdat.htm

import math

pth = '1001000070_al_136_hf_without_louver.ldt'
# pth = 'modified_file.ldt'

I_TYPE_VALUES = {
    1: 'point source with symmetry about the vertical axis',
    2: 'linear luminaire',
    3: 'point source with any other symmetry',
}

I_SYM_VALUES = {
    0: 'no symmetry',
    1: 'symmetry about the vertical axis',
    2: 'symmetry to plane C0-C180',
    3: 'symmetry to plane C90-C270',
    4: 'symmetry to plane C0-C180 and to plane C90-C270',
}


class LampSet:
    def __init__(self, lamps_number, lamps_type, total_luminous_flux, color_appearance, color_rendering_group, wattage):
        self.lamps_number = lamps_number
        self.lamps_type = lamps_type
        self.total_luminous_flux = total_luminous_flux
        self.color_appearance = color_appearance
        self.color_rendering_group = color_rendering_group
        self.wattage = wattage

    @property
    def efficiency(self):
        # EXCEL: Cells(22, 6)
        if self.wattage:
            return self.total_luminous_flux / self.wattage
        return 0

    def __str__(self):
        return "LampSet {}x{} {}W".format(self.lamps_number, self.lamps_type, self.wattage)


def get_clear_line(file_p):
    string = file_p.readline().strip()
    return string if string else 0


def get_mc_values(i_sym, mc_number):
    if i_sym == 0:
        return 1, mc_number
    elif i_sym == 1:
        return 1, 1
    elif i_sym == 2:
        return 1, mc_number / 2 + 1
    elif i_sym == 3:
        return 3 * mc_number / 4 + 1
    elif i_sym == 4:
        return 1, mc_number / 4 + 1
    else:
        raise ValueError("Invalid symmetry indicator")


class LuminaireObj:

    def __init__(self, filepath):
        with open(filepath, 'r') as f:
            # 1. Company identification
            self.company_name = get_clear_line(f)

            # 2. Type indicator Ityp
            self.i_type = int(get_clear_line(f))

            # 3. Symmetry indicator Isym || EXCEL: symm
            self.i_sym = int(get_clear_line(f))

            # 4. Number Mc of C-planes || EXCEL: M
            self.mc_number = int(get_clear_line(f))

            # 5. Distance Dc between C-planes
            self.c_planes_distance = float(get_clear_line(f))

            # 6. Number Ng of luminous intensities in each C-plane || EXCEL: N
            self.ng_number = int(get_clear_line(f))

            # 7. Distance Dg between luminous intensities per C-plane
            self.dg_distance = float(get_clear_line(f))

            # 8. Measurement report number
            self.mes_report_number = float(get_clear_line(f))

            # 9. Luminaire name
            self.lum_name = get_clear_line(f)

            # 10. Luminaire number
            self.lum_number = get_clear_line(f)

            # 11. File name
            self.file_name = get_clear_line(f)

            # 12. Date / user
            self.date_user = get_clear_line(f)

            # 13. Length/diameter of luminaire (mm)
            self.lum_lenght = float(get_clear_line(f))

            # 14. Width of luminaire b (mm) (b = 0 for circular luminaire)
            self.lum_width = float(get_clear_line(f))

            # 15. Height of luminaire (mm)
            self.lum_height = float(get_clear_line(f))

            # 16. Length/diameter of luminous area (mm) || EXCEL: Dlum
            self.luminous_area = float(get_clear_line(f))

            # 17. Width of luminous area b1 (mm) (b1 = 0 for circular luminous area of luminaire) || EXCEL: Wlum
            self.luminous_area_width = float(get_clear_line(f))

            # 18. Height of luminous area C0-plane (mm)
            self.luminous_area_c0_height = float(get_clear_line(f))

            # 19. Height of luminous area C90-plane
            self.luminous_area_C90_height = float(get_clear_line(f))

            # 20. Height of luminous area C180-plane (mm)
            self.luminous_area_C180_height = float(get_clear_line(f))

            # 21. Height of luminous area C270-plane (mm)
            self.luminous_area_C270_height = float(get_clear_line(f))

            # 22. Downward flux fraction DFF (%) || EXCEL: Kdown
            self.DFF = float(get_clear_line(f))

            # 23. Light output ratio luminaire LORL (%)
            self.LORL = float(get_clear_line(f))

            # 24. Conversion factor for luminous intensities
            self.intensities_conversion_factor = float(get_clear_line(f))

            # 25. Tilt of luminaire during measurement (road lighting luminaires)
            self.luminaire_measurement_tilt = float(get_clear_line(f))

            # 26. Number n of standard sets of lamps (optional, also extendable on company-specific basis)
            self.lamps_sets_number = int(get_clear_line(f))
            self.lamps_sets = []
            for _ in range(self.lamps_sets_number):
                # Excel ignores the fact that lamp_sets is array and uses only first lamp set
                # 26a. Number of lamps
                lamps_number = int(get_clear_line(f))

                # 26b. Type of lamps
                lamps_type = get_clear_line(f)

                # 26c. Total luminous flux of lamps (lumens)
                total_luminous_flux = float(get_clear_line(f))

                # 26d. Color appearance / color temperature of lamps || EXCEL: CCT Cells(18, 9)
                color_appearance = int(get_clear_line(f))

                # 26e. Color rendering group / color rendering index
                color_rendering_group = get_clear_line(f)

                # 26f. Wattage including ballast (watts)
                wattage = float(get_clear_line(f))

                self.lamps_sets.append(LampSet(lamps_number, lamps_type, total_luminous_flux, color_appearance,
                                          color_rendering_group, wattage))

            # 27. Direct ratios DR for room indices k = 0.6 ... 5
            # (for determination of luminaire numbers according to utilization factor method)
            self.direct_ratios = []
            for j in range(10):
                self.direct_ratios.append(float(get_clear_line(f)))

            # 28. Angles C (beginning with 0 degrees)
            self.c_angles = []
            for j in range(self.mc_number):
                self.c_angles.append(float(get_clear_line(f)))

            # 29. Angles G (beginning with 0 degrees)
            self.g_angles = []
            for j in range(self.ng_number):
                self.g_angles.append(int(get_clear_line(f)))

            # 30. Luminous intensity distribution (candela / 1000 lumens)
            self.luminous_intensity_distribution = []
            self.mc1, self.mc2 = get_mc_values(self.i_sym, self.mc_number)
            for y in range(self.mc2 - self.mc1 + 1):
                temp = []
                for j in range(self.ng_number):
                    temp.append(float(get_clear_line(f)))
                self.luminous_intensity_distribution.append(temp)


a = LuminaireObj(pth)
 for i in a.__dict__:
     if i != 'luminous_intensity_distribution':
         print i, getattr(a, i)



M = a.mc_number
N = a.ng_number

ph = a.c_angles
th = a.g_angles
print th
# I1 and I2 arrays creation

I0, I90, I180, I270 = [], [], [], []
N90 = th.index(90)

if a.i_sym == 0:
    I0 = a.luminous_intensity_distribution[0]
    I90 = a.luminous_intensity_distribution[int(M / 4)]
    I180 = a.luminous_intensity_distribution[int(M / 2)]
    I270 = a.luminous_intensity_distribution[int(3 * M / 4)]
elif a.i_sym == 1:
    for i in range(N):
        I0.append(a.luminous_intensity_distribution[0][i])
    I90, I180, I270 = I0, I0, I0
elif a.i_sym == 2:
    for i in range(N):
        I0.append(a.luminous_intensity_distribution[0][i])
        I90.append(a.luminous_intensity_distribution[int(M / 4)][i])
        I180.append(a.luminous_intensity_distribution[int(M / 2)][i])
    I270 = I90
elif a.i_sym == 3:
    for i in range(N):
        I0.append(a.luminous_intensity_distribution[int(M / 4)][i])
        I90.append(a.luminous_intensity_distribution[int(M / 2)][i])
        I270.append(a.luminous_intensity_distribution[0][i])
    I180 = I0
elif a.i_sym == 4:
    I0 = a.luminous_intensity_distribution[0]
    I90 = a.luminous_intensity_distribution[int(M / 4)]
    I180 = I0
    I270 = I90

I1, I2, th1 = [], [], []

for i in range(N90):
    I1.append(I0[i])
    I2.append(I90[i])
    th1.append(th[i])

for i in range(N90, 2 * N90):
    I1.append(I180[2 * N90 - i])
    I2.append(I270[2 * N90 - i])
    th1.append(th[2 * N90 - i] * -1)


final_arr = []
final_arr2 = []
for i in range(len(th1)):
    final_arr.append([th1[i], I1[i]])
    final_arr2.append([th1[i], I2[i]])


#  GRAPHIC DISPLAYING ON FRONTEND


# Min, max and avg of light force curve for first main plane determination
Imax, Imin, Io = max(I1[:2*N90+1]), min(I1[:N90+1]), sum(I1[:2*N90+1]) / len(I1[:2*N90+1])
ithmax = I1.index(Imax)


def get_lfc_type(Imax, Io, th1, arr):
    lfc_type = ''  # | EXCEL Cells(13, 8)
    if Imax / Io >= 3 and abs(th1[ithmax]) <= 15:
        lfc_type = "К-концетрированная"
    elif 3 > Imax / Io >= 2 and abs(th1[ithmax]) <= 30:
        lfc_type = "Г-глубокая"
    elif 2 > Imax / Io >= 1.3 and abs(th1[ithmax]) <= 35:
        lfc_type = "Д-косинусная"
    elif 2 > Imax / Io >= 1.3 and 35 < abs(th1[ithmax]) <= 55:
        lfc_type = "Л-полуширокая"
    elif 3.5 > Imax / Io >= 1.5 and 55 < abs(th1[ithmax]) <= 85:
        lfc_type = "Ш-широкая"
    elif Imax / Io <= 1.3 and Imin > 0.7 * Imax:
        lfc_type = "М-равномерная"
    elif Imax / Io > 1.3 and arr[0] < 0.7 * Imax and abs(th1[ithmax]) >= 70:
        lfc_type = "С-синусная"
    return lfc_type


# Light force curve type for first main plane determination
lfc1 = get_lfc_type(Imax, Io, th1, I1)


# Opening angle for the first main plane determination
def get_opening_angle(ithmax, N90, Imax, th1, I1):
    thplus = 900
    thminus = 900
    iplus1, iminus1 = 0, 0

    if ithmax <= N90:
        for i in range(ithmax, N90):
            if I1[i] > 0.5 * Imax >= I1[i + 1]:
                thplus = th1[i]
                iplus1 = i

        for i in range(N90 + 1, N90 * 2 - 1):
            if I1[i] <= 0.5 * Imax < I1[i + 1]:
                thminus = th1[i]
                iminus1 = i

        if thminus == 900:
            for i in range(ithmax):
                if I1[i] <= 0.5 * Imax < I1[i + 1]:
                    thminus = th1[i]
                    iminus1 = i
    else:
        for i in range(ithmax, N90 * 2):
            if I1[i] > 0.5 * Imax >= I1[i + 1]:
                thplus = th1[i]
                iplus1 = i

        for i in range(N90):
            if I1[i] > 0.5 * Imax >= I1[i + 1]:
                thplus = th1[i]
                iplus1 = i

        for i in range(N90 + 1, ithmax - 1):
            if I1[i] <= 0.5 * Imax < I1[i + 1]:
                thminus = th1[i]
                iminus1 = i
    return abs(thplus - thminus)


opening_angle_1 = get_opening_angle(ithmax, N90, Imax, th1, I1)  # | EXCEL Cells(11, 8)

# overall brightness for the first main plane determination
Dlum = abs(a.lum_lenght)
Wlum = abs(a.lum_width)
F = a.lamps_sets[0].total_luminous_flux
H0 = a.luminous_area_c0_height


def get_overall_brightness(F, H0, Dlum, Wlum, th, I1):
    overall_brightness = []
    print len(th), N90
    if Dlum != 0:
        if Wlum != 0:
            for i in range(2 * N90):
                overall_brightness.append(
                    I1[i] * F * 1000 / (Dlum * Wlum * abs(math.cos(round(math.pi * th[i] / 180, 3))) + Dlum * H0 *
                                        abs(math.sin(math.pi * th[i] / 180)))
                )
        else:
            for i in range(2 * N90):
                overall_brightness.append(
                    I1[i] * F * 1000 / (Dlum ** 2 * 0.25 * math.pi * abs(math.cos(round(math.pi * th[i] / 180, 3))) +
                                        Dlum * H0 * abs(math.sin(math.pi * th[i] / 180)))
                )
    return overall_brightness

overall_brightness1 = get_overall_brightness(F, H0, Dlum, Wlum, th1, I1)

# Min, max and avg of light force curve for second main plane determination
Imax, Imin, Io = max(I2[:2*N90+1]), min(I2[:N90+1]), sum(I2[:2*N90+1]) / len(I2[:2*N90+1])
ithmax = I2.index(Imax)

lfc2 = get_lfc_type(Imax, Io, th1, I2) # | EXCEL Cells(13, 10)

opening_angle2 = get_opening_angle(ithmax, N90, Imax, th1, I2)  # | EXCEL Cells(11, 10)

overall_brightness2 = get_overall_brightness(F, H0, Dlum, Wlum, th1, I2)

overall_brightness_final_arr1 = []
overall_brightness_final_arr2 = []

for i in range(len(th1[1:])):
    overall_brightness_final_arr1.append([th1[i], overall_brightness1[i]])
    overall_brightness_final_arr2.append([th1[i], overall_brightness2[i]])


thEYE = 45 # now default, later get from request

CCT_ranges = [
    [0, 2350], [2350, 2850], [2850, 3250], [3250, 3750], [3750, 4500], [4500, 5750], [5750, 8000]
]
CCT_values = [4000, 1850, 1450, 1100, 850, 650, 500]

H90 = 0
CCT = a.lamps_sets[0].color_appearance
cctIND = 0
Leye = 0
key1, key2 = 0, 0
risk_group = 0
risk_distance = []

if 0 < CCT:
    for i in CCT_ranges:
        if i[0] <= CCT < i[1]:
            # index of row to show
            cctIND = CCT_ranges.index(i)
            break
    LeyeMAX = 0
        if Dlum != 0:
            if Wlum != 0:
                val2 = Dlum * Wlum * abs(math.cos(round(math.pi, 5) * th1[int(1 + N * th_eye / 180)] / 180))
                val4 = abs(math.sin(round(math.pi, 5) * th1[int(1 + N * th_eye / 180)] / 180))
                for j in range(M):
                    leye = a.luminous_intensity_distribution[int(len(a.luminous_intensity_distribution)/4)][j] * F *\
                           1000 / (val2 + (Dlum * H0 * abs(math.cos(ph[j] / 180)) + Wlum * H90 * abs(
                               math.sin(ph[j] / 180))) * val4)
                    if leye > leye_max:
                        leye_max = leye
                        lmax_ind = j
            else:
                val2 = Dlum ** 2 * 0.25 * round(math.pi, 5) * abs(math.cos(round(math.pi, 5) *
                                                                           th1[int(1 + N * th_eye / 180)] / 180))
                val4 = abs(math.sin(round(math.pi, 5) * th1[int(1 + N * th_eye / 180)] / 180))
                for j in range(M):
                    leye = a.luminous_intensity_distribution[int(len(a.luminous_intensity_distribution)/4)][j] * F *\
                           1000 / (val2 + (0.5 * round(math.pi, 5) * Dlum * H0) * val4)
                    if leye > leye_max:
                        leye_max = leye
                        lmax_ind = j
            if leye_max > 10000:
                key1 = 1
    # Яркость кд/м2 | EXCEL Cells(29, 8)
    brightness = int(LeyeMAX)

    if key1 == 1:
        if a.luminous_intensity_distribution[LmaxIND][int(N * thEYE / 180)] * F * 0.001 / 0.5 ** 2 > \
                CCT_values[cctIND]:
            key2 = 2
    else:
        risk_group = 0

    if key1 == 1:
        if key2 == 2:
            risk_group = 2
            for i in range(len(CCT_values)):
                risk_distance.append(round(math.sqrt(a.luminous_intensity_distribution[LmaxIND][int(N * thEYE / 180)] *
                                               F * 0.001 / CCT_values[i]), 1))
        else:
            risk_group = 1

    print brightness, risk_distance, risk_group, cctIND
