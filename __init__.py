def classFactory(iface):
    from .pixel_energy import PixelEnergy
    return PixelEnergy(iface)