Hisense_RGB_to_XYZ_matrix = np.matrix(colour.models.normalised_primary_matrix(
    [0.679,0.3126,0.194,0.6954,0.1515,0.0640], [0.3127,0.3290]))
Hisense_XYZ_to_RGB_matrix = np.linalg.inv(Hisense_RGB_to_XYZ_matrix)

with open('/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/HDR ST 2084/Magic.cube', 'w') as fp:
    fp.write('LUT_3D_SIZE 64\n')
    #fp.write('LUT_3D_INPUT_RANGE 0.0000000000 1.0000000000\n\n')
    smpte_tf = SMPTE2084TransferFunc(1000)
    gamma_tf = GammaTransferFunc(2.6)

    for bi in np.linspace(0,1,64):
        for gi in np.linspace(0,1,64):
            for ri in np.linspace(0,1,64):
                rl, gl, bl = map(smpte_tf.eotf, [ri, gi, bi])
                rc, gc, bc = np.array(Hisense_XYZ_to_RGB_matrix.dot(
                    colour.models.REC_2020_COLOURSPACE.RGB_to_XYZ_matrix.dot(
                        [rl, gl, bl])))[0]
                rg, gg, bg = map(gamma_tf.oetf, [rc, gc, bc])
                rn, gn, bn = map(lambda v: 1. if v > 1 else (v if v > 0 else 0.), [rg, gg, bg])

                fp.write("%s %s %s\n" % (rn, gn, bn))

