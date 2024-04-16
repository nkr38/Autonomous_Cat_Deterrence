#%%
from Camera import Camera

#%%
cam = Camera()
#%%
cam.start_recording()
#%%
print(cam.capture_main().shape)
print(cam.capture_main(1).shape)
#%%
print(cam.capture_lores().shape)
print(cam.capture_lores(1).shape)
# %%
cam.stop_recording()

# %%
