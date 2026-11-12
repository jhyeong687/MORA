#!/usr/bin/env python3
"""Build a local RViz shader workaround only when the renderer supports it.

Mesa validates mixed sampler types before OGRE sets uniform bindings. Explicit
bindings avoid the collision. Never modify the installed ROS package; preserve
the upstream shader on renderers without ARB_shading_language_420pack.
"""
import json
import os
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent


def main():
    metadata={'workaround_enabled':False,'installed_ros_modified':False}
    try:
        os.environ['QT_QPA_PLATFORM']='xcb'
        from PyQt5.QtGui import QGuiApplication,QOpenGLContext,QOffscreenSurface,QOpenGLShader,QOpenGLShaderProgram
        app=QGuiApplication([]);ctx=QOpenGLContext()
        if not ctx.create():raise RuntimeError('OpenGL context unavailable')
        surface=QOffscreenSurface();surface.setFormat(ctx.format());surface.create()
        if not ctx.makeCurrent(surface):raise RuntimeError('OpenGL offscreen context unavailable')
        if b'GL_ARB_shading_language_420pack' not in {bytes(e) for e in ctx.extensions()}:
            raise RuntimeError('Renderer lacks explicit sampler bindings; using upstream shader')
        source=Path('/opt/ros/jazzy/share/rviz_rendering')
        relative=Path('ogre_media/materials/glsl120/indexed_8bit_image.frag')
        frag=(source/relative).read_text().replace('#version 120','#version 120\n#extension GL_ARB_shading_language_420pack : require')
        frag=frag.replace('uniform sampler2D','layout(binding = 0) uniform sampler2D').replace('uniform sampler1D','layout(binding = 1) uniform sampler1D')
        program=QOpenGLShaderProgram()
        if not (program.addShaderFromSourceCode(QOpenGLShader.Vertex,(source/relative.with_suffix('.vert')).read_text()) and
                program.addShaderFromSourceCode(QOpenGLShader.Fragment,frag) and program.link()):
            raise RuntimeError('Shader compile/link failed: '+program.log())
        overlay=ROOT/'generated/rviz_overlay';destination=overlay/'share/rviz_rendering'
        shutil.copytree(source,destination,dirs_exist_ok=True);(destination/relative).write_text(frag)
        marker=overlay/'share/ament_index/resource_index/packages/rviz_rendering'
        marker.parent.mkdir(parents=True,exist_ok=True);marker.write_text('')
        metadata.update({'workaround_enabled':True,'overlay':str(overlay),'gl_version':[ctx.format().majorVersion(),ctx.format().minorVersion()]})
    except Exception as exc:metadata['reason']=str(exc)
    (ROOT/'generated/rviz_renderer.json').write_text(json.dumps(metadata,indent=2))
    print('RViz renderer:',json.dumps(metadata))


if __name__=='__main__':main()
