def e3(A, B, C, n=7):
    '''Return centered at the midpoint of A and C with the axis going through B if the angle at B is acute, else going through A and C.
    '''
    from sympy import Line
    xc, yc = ctr = (A + C)/2
    AC = A.distance(C)
    smalls = True
    if AC >= B.distance(A) and AC >= B.distance(C):
        s = Line(A, C).slope
        M2 = ctr.distance(A)**2
        b = B
        if abs(s) <= 1:
            m2 = -M2*(s*(b.x - xc) - b.y + yc)**2/(
                -M2*(s**2 + 1) + (s*(b.y - yc) + b.x - xc)**2)
        else:
            s = 1/s
            m2 = M2*(s*(b.y - yc) - b.x + xc)**2/(
                M2*(s**2 + 1) - (s*(b.x - xc) + b.y - yc)**2)
            smalls = False
    else:
        s = Line(B, ctr).slope
        M2 = ctr.distance(B)**2
        p = A # or C
        if abs(s) <= 1:
            m2 = -M2*(s*(p.x - xc) - p.y + yc)**2/(
                -M2*(s**2 + 1) + (s*(p.y - yc) + p.x - xc)**2)
        else:
            s = 1/s
            m2 = M2*(s*(p.y - yc) - p.x + xc)**2/(
                M2*(s**2 + 1) - (s*(p.x - xc) + p.y - yc)**2)
            smalls = False
    if smalls:
        el = -1 + (-s*(x - xc) + p.y - yc)**2/(m2*(s**2 + 1)) + (
            s*(p.y - yc) + x - xc)**2/(M2*(s**2 + 1))
    else:
        el = (M2*(s**2 + 1)*(-m2*(s**2 + 1) + (s*(p.y - yc) - x + xc)**2
            ) + m2*(s**2 + 1)*(s*(x - xc) + p.y - yc)**2)/(
            M2*m2*(s**2 + 1)**2)
    return el.expand().n(n=n)

from sympy import Point
a,b,c = Point(7/5, 12/5), Point(3/2, 5/2), Point(19/10, 3/2)
e3(a,b,c)
e3(b,c,a)
e3(c,a,b)