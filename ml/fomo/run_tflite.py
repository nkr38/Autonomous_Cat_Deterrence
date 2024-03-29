# %% 
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
# %% 
model_path = "models/ei-catfomo2-object-detection-tensorflow-lite-int8-quantized-model.lite"


interpreter = tf.lite.Interpreter(model_path=model_path)
# %% 

runner = interpreter.get_signature_runner()

# %%
fname = "../../data/raspi_frames/cat_counter1_frame18.png"
pil_img = ImageOps.grayscale(Image.open(fname)).resize((96, 96))
sample_input = np.array(pil_img, dtype=np.int8)
sample_input = np.reshape(sample_input, newshape=(1, 96, 96, 1))
#%%
out = runner(x = sample_input)


# %%
outimg = Image.fromarray(np.reshape(out['output_0'][:,:,:,0],(12,12)))
outimg2 = Image.fromarray(np.reshape(out['output_0'][:,:,:,1],(12,12)))

# %%
display(outimg)
display(outimg2)
#%%