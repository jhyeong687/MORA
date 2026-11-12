from pathlib import Path
import adsk.core

def run(context):
    app=adsk.core.Application.get()
    ui=app.userInterface
    here=Path(__file__).resolve().parent
    choices=(here/'Resources'/'R4_3D_Playback.html', here.parent.parent/'R4_3D_Playback.html')
    page=next((p for p in choices if p.is_file()),None)
    if page is None:
        ui.messageBox('키트에서 R4_3D_Playback.html과 Fusion 폴더를 함께 압축 해제해 주세요.')
        return
    palette=ui.palettes.itemById('R4MotionPreview')
    if palette is None:
        palette=ui.palettes.add('R4MotionPreview','R4 · 조립과 로봇팔 동작',page.as_uri(),True,True,True,900,700)
    else:
        palette.htmlFileURL=page.as_uri()
        palette.isVisible=True
