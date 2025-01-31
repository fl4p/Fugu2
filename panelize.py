from kikit.common import KiPoint
from kikit.panelize import Panel, expandRect, findBoardBoundingBox, pcbnew, Origin
from kikit.plugin import LayoutPlugin
from kikit.units import mm

class Plugin(LayoutPlugin):
    def buildLayout(self, panel: Panel, mainInputFile: str, _sourceArea):
        layout = self.preset["layout"]

        cols = layout.get("cols", None)
        if not cols:
            raise RuntimeError("Specify the number of colums like this: --layout '...; cols: 3'")
        cols = int(cols)

        boards = layout.get("boards", None)
        if not boards:
            raise RuntimeError("Specify the boards and counts like this: --layout '...; boards: board_a.kicad_pcb, 3*board_b.kicad_pcb'")

        panel.sourcePaths.add(mainInputFile)

        netRenamer = lambda n, orig: self.netPattern.format(n=n, orig=orig)
        refRenamer = lambda n, orig: self.refPattern.format(n=n, orig=orig)

        col = x = y = next_y = 0
        for filename in boards.split(","):
            parts = filename.split("*", 1)
            filename = parts[-1].strip()
            count = 1 if len(parts) == 1 else int(parts[0])

            for _ in range(count):
                board = pcbnew.LoadBoard(filename)

                size = panel.appendBoard(
                    filename=filename,
                    destination=KiPoint(x, y),
                    sourceArea=expandRect(findBoardBoundingBox(board), 1 * mm),
                    netRenamer=netRenamer,
                    refRenamer=refRenamer,
                    rotationAngle=self.rotation,
                    inheritDrc=False,
                )

                col += 1
                if col == cols:
                    col = x = 0
                    y = next_y
                else:
                    x += size.GetWidth() + self.vspace
                    next_y = max(next_y, y + size.GetHeight() + self.hspace)

        return panel.substrates


layout_desc = [
    dict(pcb='Fugu2.kicad_pcb', count=1, rotation=0 ),
    dict(pcb='psu/buck100.kicad_pcb', count=2, rotation=90),
    dict(pcb='../hw/precision-current-sensor/precision-current-sensor.kicad_pcb', count=1),
]


class Plugin2(LayoutPlugin):
    def buildLayout(self, panel: Panel, mainInputFile: str, _sourceArea):
        layout = self.preset["layout"]


        #boards = layout.get("boards", None)
        #if not boards:
        #    raise RuntimeError("Specify the boards and counts like this: --layout '...; boards: board_a.kicad_pcb, 3*board_b.kicad_pcb'")

        panel.sourcePaths.add(mainInputFile)

        netRenamer = lambda n, orig: self.netPattern.format(n=n, orig=orig)
        refRenamer = lambda n, orig: self.refPattern.format(n=n, orig=orig)

        col = x = y = next_y = 0

        max_cols = 10

        for d in layout_desc:
            filename = d['pcb']
            count = int(d.get('count', 1))
            assert count > 0
            rotation = int(d.get('rotation', 0))

            for _ in range(count):
                board = pcbnew.LoadBoard(filename)

                size = panel.appendBoard(
                    filename=filename,
                    destination=KiPoint(x, y),
                    origin=Origin.TopRight if rotation == 90 else Origin.TopLeft,
                    sourceArea=expandRect(findBoardBoundingBox(board), 1 * mm),
                    netRenamer=netRenamer,
                    refRenamer=refRenamer,
                    rotationAngle=self.rotation +  pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T),
                    inheritDrc=False,
                )

                col += 1
                if col == max_cols:
                    col = x = 0
                    y = next_y
                else:
                    x += size.GetWidth() + self.vspace
                    next_y = max(next_y, y + size.GetHeight() + self.hspace)

            x = 0
            y = next_y

        return panel.substrates