from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from math import sqrt


def crop_images(image_path, fild=5):
    img = QImage(image_path, '.jpg')
    for each_side in range(4):
        width = img.width()
        height = img.height()
        fild_real = 0
        for row in range(height):
            row_res = all([QColor(img.pixel(i, row)).getRgb()[:3] == (0, 0, 0) for i in range(width)])
            if not row_res:
                break
            else:
                fild_real += 1
        img = img.copy(0, fild_real - fild, width, height - (fild_real - fild))
        img = img.transformed(QMatrix().rotate(-90.0))
    img.save(image_path)
    return img


def render_icon(width=200):
    # render setup
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware", type="string")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8)

    ct = cmds.ls(sl=True)[0]
    # get size and make profile
    a = cmds.getAttr(ct + '.boundingBoxMin')[0]
    b = cmds.getAttr(ct + '.boundingBoxMax')[0]
    xy = sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]))
    size = sqrt(xy * xy + (a[2] - b[2]) * (a[2] - b[2]))
    profile = cmds.circle(r=size / 200, nr=(0, 1, 0))[0]

    # make shader
    shader = cmds.shadingNode('surfaceShader', asShader=True)
    shaderSG = cmds.sets(name='%sSG' % shader, empty=True, renderable=True, noSurfaceShader=True)
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shaderSG)
    cmds.setAttr(shader + ".outColor", 1, 1, 1)
    nodes_for_del = [shader, shaderSG, profile]

    # make render geo
    shapes = cmds.listRelatives(ct, s=True)
    for shape in shapes:
        crv_rebuild = cmds.rebuildCurve(shape, ch=True, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=400, d=1,
                                        tol=0.01)
        nodes_for_del += crv_rebuild
        geo = cmds.extrude(profile, crv_rebuild[0], rn=True, po=0, et=2, ucp=1, fpt=1, upn=1, rsp=1)
        cmds.sets(geo[0], e=True, forceElement=shaderSG)
        nodes_for_del += geo

    image_path = cmds.render("persp", x=500, y=500)
    img = crop_images(image_path, fild=20)
    img = img.transformed(QMatrix().scale(0.5))
    img.save(image_path)

    cmds.delete(nodes_for_del)   