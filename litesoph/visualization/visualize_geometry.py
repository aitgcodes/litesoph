import subprocess

class VisualizationFailed(RuntimeError):
    """ Raised when geometry rendering fails """


class VisualizeGeometry:

    def __init__(self, lsconfig_vis_tools) -> None:
        path = lsconfig_vis_tools.get('vmd', None)
        if not path:
            path = lsconfig_vis_tools.get('vesta', None)
        if not path:
            path = 'vmd'
        self.vis_tool = path

    def render(self, geometry_file):
        cmd = self.vis_tool + ' ' + str(geometry_file)
        try:
            subprocess.run(cmd.split(),capture_output=True)
        except Exception as e:
            raise VisualizationFailed(f"Error: {e}.Command used to call visualization program '{self.vis_tool}'. supply the appropriate command in ~/.litesoph/lsconfig.ini.")