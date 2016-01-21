def dumbsum(v):
    return 256 - (sum(v) & 0xff)

def enc(rx=0.68, ry=0.320, gx=0.265, gy=0.69, bx=0.15, by=0.06, wx=0.3127, wy=0.329,
        dmax=4000, dmin=0.0005, maxcll=500, maxfall=400, include_maxcll=True):
    vals = ([int(round(v / 0.00002)) for v in [rx, ry, gx, gy, bx, by, wx, wy]] +
            [int(v) for v in [dmax, dmin / 0.0001, maxcll, maxfall]])
    outdata = [0x02, 0x00] + sum([[v & 0xff, v >> 8] for v in vals], [])
    if not include_maxcll:
        outdata = outdata[:-4]
    outdata = [0x87, 0x01, len(outdata) + 1, 0] + outdata
    outdata[3] = dumbsum(outdata)
    return ':'.join(['%02X' % v for v in outdata])

# Print a few variations for spot-checking
print(enc())
print(enc(include_maxcll=False))
print('87:01:17:5c:02:00:D0:84:80:3E:C2:33:C4:86:4C:1D:B8:0B:13:3D:42:40:A0:0F:05:00')

# No change on the LG from the above, that I could tell at a glance
print(enc(dmax=500, include_maxcll=False))

print('BVM-X300:')
# dmin is really 0 but I think that causes divide-by-zero in LUT generation somewhere
print(enc(dmax=1000, dmin=0.0001, maxcll=1000, maxfall=600))
