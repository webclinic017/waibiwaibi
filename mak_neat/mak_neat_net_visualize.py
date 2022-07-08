# @ last edit time 2022/1/26 0:14

import numpy as np
import math

from PIL import Image, ImageDraw, ImageFont

from mak_neat_net import neat_net, gene_node_id


def cover_circle(array_img, size, start, color):
    x0 = start[0]
    y0 = start[1]
    r = int(size / 2)
    for x in range(max(0, x0 - r), min(array_img.shape[1] - 1, x0 + r)):
        for y in range(max(0, y0 - r), min(array_img.shape[0] - 1, y0 + r)):
            if (x - x0) ** 2 + (y - y0) ** 2 <= r ** 2:
                array_img[y][x] = color


def cover_line(array_img, size, start, end, color):
    if start[0] <= end[0]:
        x1, x2 = start[0], end[0]
        y1, y2 = start[1], end[1]
    else:
        x1, x2 = end[0], start[0]
        y1, y2 = end[1], start[1]
    if x2 - x1 == 0:
        k = 1000
    elif y2 - y1 == 0:
        k = 1 / 1000
    else:
        k = (y2 - y1) / (x2 - x1)
    angle = math.atan(abs(k))
    size_y = size / 2 / max(math.cos(angle), math.sin(angle))

    k = - 1 / k if k < 0 else k
    limit_up_1 = lambda x: int((x - x1) * k + y1 + size_y)
    limit_down_1 = lambda x: int((x - x1) * (- 1 / k) + y1 - size_y)
    limit_up_2 = lambda x: int((x - x2) * (- 1 / k) + y2 + size_y)
    limit_down_2 = lambda x: int((x - x2) * k + y2 - size_y)

    for x in range(max(0, x1 - size), min(array_img.shape[1] - 1, x2 + size)):
        for y in range(max(0, limit_down_1(x), limit_down_2(x)),
                       min(array_img.shape[0] - 1, limit_up_1(x), limit_up_2(x))):
            array_img[y][x] = color


def color_mix(color1, color2, rate):
    res = ()
    for i in range(len(color1)):
        channel = int(rate * color1[i] + (1 - rate) * color2[i])
        channel = 255 if channel > 255 else channel
        channel = 0 if channel < 0 else channel
        res += (channel,)
    return res


# def net_visualize(net: neat_net, dir_img: str, grid_size=200, node_size=40, connection_size=6, char_size=20):
#     image_width = grid_size * (len(net.net) + 2)
#     image_height = grid_size * (max([len(x) for x in net.net]) + 2)
#     array_output = np.ones([image_height, image_width, 3], dtype=np.int32) * 255
#     node_location = lambda x, y: np.array([grid_size * (x + 1), int(image_height / 2 + grid_size * (y - len(net.net[x]) / 2))])
#     for i in range(len(net.net)):
#         for j in range(len(net.net[i])):
#             cover_circle(array_output, node_size, node_location(i, j), (0, 0, 0))
#
#     print(net.masks)
#     print(net.matrixs)
#     for i in range(len(net.masks)):
#         for j in range(len(net.masks[i])):
#             for fi in range(len(net.masks[i][j])):
#                 for fj in range(len(net.masks[i][j][fi])):
#                     if net.masks[i][j][fi][fj]:
#                         red = np.array([255, 0, 0])
#                         yellow = np.array([255, 255, 0])
#                         green = np.array([0, 255, 255])
#                         sigmoid = lambda x: math.tanh(x)
#                         value = net.matrixs[i][j][fi][fj]
#                         if value >= 0:
#                             color = sigmoid(value) * red + (1 - sigmoid(value)) * yellow
#                         else:
#                             color = sigmoid(-value) * green + (1 - sigmoid(-value)) * yellow
#                         for ch in range(color.shape[0]):
#                             color[ch] = int(color[ch])
#                             if color[ch] > 255:
#                                 color[ch] = 255
#                             if color[ch] < 0:
#                                 color[ch] = 0
#                         print(fi, fj, i+1, j)
#                         print(value)
#                         print(sigmoid(value))
#                         print(color)
#                         cover_line(array_output, connection_size, node_location(fi, fj) + [int(node_size/2), 0],
#                                    node_location(i+1, j) - [int(node_size/2), 0], color)
#
#     image_output = Image.fromarray(array_output.astype('uint8')).convert('RGB')
#     image_output.save(dir_img, 'bmp')


def net_visualize(net: neat_net, dir_img: str, grid_size=200, node_size=40, connection_size=6, char_size=20):
    image_width = grid_size * (len(net.net) + 2)
    image_height = grid_size * (max([len(x) for x in net.net]) + 2)
    image_output = Image.fromarray((np.ones([image_height, image_width, 3]) * 255).astype('uint8')).convert('RGB')
    image_draw = ImageDraw.Draw(image_output)

    node_location = lambda x, y: (grid_size * (x + 1), int(image_height / 2 + grid_size * (y - len(net.net[x]) / 2)))

    font = ImageFont.truetype('arial.ttf', size=int(node_size / 2))
    r = int(node_size / 2)
    for i in range(len(net.net)):
        for j in range(len(net.net[i])):
            x, y = node_location(i, j)
            image_draw.ellipse((x - r, y - r, x + r, y + r), fill=(0, 0, 0, 0))
            font_x, font_y = font.getsize(str(net.net[i][j]))
            image_draw.text((x - int(font_x / 2), y - int(font_y / 2)), str(net.net[i][j]), font=font, fill=(255, 255, 255))
            node = gene_node_id(net.chrom.gen_nodes, net.net[i][j])
            if node:
                font_x, font_y = font.getsize(node.activation_func)
                image_draw.text((x - int(font_x / 2), y + 2 * r - int(font_y / 2)), node.activation_func, font=font, fill=(0, 0, 0))


    red = (255, 0, 0, 0)
    yellow = (255, 255, 0, 0)
    green = (0, 255, 255, 0)
    sigmoid = lambda x: math.tanh(x)
    for i in range(len(net.masks)):
        for j in range(len(net.masks[i])):
            for fi in range(len(net.masks[i][j])):
                for fj in range(len(net.masks[i][j][fi])):
                    if net.masks[i][j][fi][fj]:
                        value = net.matrixs[i][j][fi][fj]
                        if value >= 0:
                            color = color_mix(red, yellow, sigmoid(value))
                        else:
                            color = color_mix(green, yellow, sigmoid(-value))
                        x, y = node_location(i+1, j)
                        fx, fy = node_location(fi, fj)
                        image_draw.line(((fx + r, fy), (x - r, y)), fill=color, width=connection_size)


    image_output.save(dir_img, 'bmp')


if __name__ == '__main__':
    from mak_neat_genome import generate_chromesome_basic

    net = neat_net(generate_chromesome_basic(4, 2))
    net_visualize(net, 'drawing_net.bmp')





