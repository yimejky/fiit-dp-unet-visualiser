
import sys
sys.path.append('../')
from pycore.tikzeng import *
from pycore.blocks  import *

def block(conv_num, pool_num, in_channels, out_channels, height, height_out, to=None, width=2, width_scaller=2):
    cn = conv_num
    pn = pool_num

    if to is None:
        offset = "(1,0,0)"
    else:
        offset = "(-1,0,0)"

    if to is None:
        to = f"(pool{pn-1}-east)"

    return [
        to_Conv(f"conv{cn}", '', in_channels, offset=offset, to=to, height=height, depth=height, width=width),
        to_Conv(f"conv{cn+1}", '', out_channels, offset="(0,0,0)", to=f"(conv{cn}-east)", height=height, depth=height, width=width*width_scaller),
        to_Pool(f"pool{pn}", offset="(0,0,0)", to=f"(conv{cn+1}-east)", height=height_out, depth=height_out, width=1),
    ]


def unblock(conv_num, pool_num, in_channels, out_channels, height, to=None, width=2, width_scaller=2):
    cn = conv_num
    pn = pool_num

    if to is None:
        to = f"(unconv{cn-1}-east)"

    return [
        to_UnPool(f"unpool{pn}", offset="(1,0,0)", to=to, height=height, depth=height, width=1),
        to_Conv(f'unconv{cn}', '', in_channels, offset="(0,0,0)", to=f"(unpool{pn}-east)", height=height, depth=height, width=width*width_scaller),       
        to_Conv(f'unconv{cn+1}', '', out_channels, offset="(0,0,0)", to=f"(unconv{cn}-east)", height=height, depth=height, width=width),
    ]

arch = [ 
    to_head( '..' ),
    to_cor(),
    to_begin(),

    to_input( './input.png' ),
]

in_ch = 16
width = 1
max_num = 4
width_scaller = 1.5
width_offset = 2
height_init = 8

max_width = width * width_scaller ** max_num
max_in_ch = in_ch * 2 ** max_num
max_height = height_init * (max_num+1)

for i in range(max_num):
    j = i+1
    tmp_in_ch = in_ch * (2**(i-1)) if i > 0 else 1
    tmp_out_ch = in_ch * (2**i) if i > 0 else in_ch
    tmp_width = width * (width_scaller**i) + width_offset
    tmp_height = height_init*(max_num-i+1)
    to = '(0,0,0)' if i <= 0 else None
    arch.extend(block(1 + i*2, j, tmp_in_ch, tmp_out_ch, height=tmp_height, height_out=tmp_height-height_init, to=to, width=tmp_width, width_scaller=width_scaller))

arch.extend([
    to_Conv("middle_conv1", '', 128, offset="(1,0,0)", to=f"(pool4-east)", height=height_init, depth=height_init, width=max_width+width_offset),
    to_Conv("middle_conv2", '', 256, offset="(0,0,0)", to=f"(middle_conv1-east)", height=height_init, depth=height_init, width=max_width*width_scaller+width_offset)
])

for i in range(max_num):
    j = i+1
    tmp_in_ch = max_in_ch // (2**i)
    tmp_out_ch = max_in_ch // (2**j)
    tmp_width = max_width / (width_scaller**i) + width_offset
    to = '(middle_conv2-east)' if i <= 0 else None
    arch.extend(unblock(1 + i*2, j, tmp_in_ch, tmp_out_ch, height=height_init*(j+1), to=to, width=tmp_width, width_scaller=width_scaller))

arch.extend([
    to_Conv("output", '', 1, offset="(1,0,0)", to=f"(unconv8-east)", height=max_height, depth=max_height, width=width + width_offset, caption="sigmoid"),
    # to_ConvSoftMax("output", 1, "(1,0,0)", to="(unconv8-east)", caption="Sigmoid",  height=max_height, depth=max_height),

    to_connection("pool1", "conv3"), 
    to_connection("pool2", "conv5"), 
    to_connection("pool3", "conv7"), 
    to_connection("pool4", "middle_conv1"), 
    to_connection("middle_conv2", "unpool1"), 
    to_connection("unconv2", "unpool2"), 
    to_connection("unconv4", "unpool3"), 
    to_connection("unconv8", "output"), 

    to_skip(of='conv2', to='unconv7', pos=1.25),
    to_skip(of='conv4', to='unconv5', pos=1.25),
    to_skip(of='conv6', to='unconv3', pos=1.25),    
    to_skip(of='conv8', to='unconv1', pos=1.25),

    to_end()
])


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
    
