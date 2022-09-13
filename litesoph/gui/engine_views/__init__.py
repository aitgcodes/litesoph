from litesoph.gui.engine_views.engine_views_abc import EngineViews

from litesoph.gui.engine_views.gpaw_views import GpawGSPage
from litesoph.gui.engine_views.nwchem_views import NWGSPage
from litesoph.gui.engine_views.octopus_views import OctGSPage

def get_gs_engine_page(engine,gspage):
    
    if engine == 'gpaw':
        return GpawGSPage(gspage)
    elif engine == 'nwchem':
        return NWGSPage(gspage)
    elif engine == 'octopus':
        return OctGSPage(gspage)