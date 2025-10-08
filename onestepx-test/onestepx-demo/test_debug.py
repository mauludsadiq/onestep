import onestepx_driver_seeded
from onestepx import TERMINAL

print("Before init_driver:")
print("  hasattr(TERMINAL, 'flags'):", hasattr(TERMINAL, 'flags'))
if hasattr(TERMINAL, 'flags'):
    print("  TERMINAL.flags keys:", list(TERMINAL.flags.keys()))
    print("  'proj_bitsets' in flags:", 'proj_bitsets' in TERMINAL.flags)

drv = onestepx_driver_seeded.init_driver()

print("\nAfter init_driver:")
print("  drv._pb:", drv._pb)
print("  type(drv._pb):", type(drv._pb))
