import matplotlib
import numpy as  np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.path as mpath
import pandas as pd
from matplotlib.collections import LineCollection
fig = plt.figure(figsize=(9, 9))

projection=ccrs.NorthPolarStereo(central_longitude=0,globe=None)

ax = fig.add_subplot(111,projection=projection)
ax.set_extent([-180, 180, 0, 90], crs=ccrs.PlateCarree())
ax.coastlines(linewidths=1, color='#9eacac')
ax.add_feature(cfeature.OCEAN, facecolor='#A0FFFF')
ax.add_feature(cfeature.LAND, facecolor='#FFFFFF')#FFFFFF
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
theta = np.linspace(0, 2 * np.pi, 100)
circle = mpath.Path(np.vstack([np.sin(theta), np.cos(theta)]).T * 0.5 + [0.5, 0.5])
ax.set_boundary(circle, transform=ax.transAxes)
dtype ={
        'province_id': int,
        'longitude': np.float32,
        'latitude': np.float32,
        'is_hole': bool
    }
df = pd.read_csv("china_province_boundaries.csv", dtype=dtype)
# 提前过滤非空洞数据
main_df = df[~df['is_hole']].copy()
# 3. 按省份分组，将每个省份的坐标转换为 numpy 数组（避免循环内转换）
# 结果格式：{province_id: (lon_array, lat_array), ...}
province_coords = {}
for province_id, group in main_df.groupby('province_id'):
    # 直接转换为 numpy 数组（比 Series 操作快）
    lons = group['longitude'].to_numpy()
    lats = group['latitude'].to_numpy()
    province_coords[province_id] = (lons, lats)
# 设置地图范围 因为中国的最低纬度是4° 所以经理说能把中国显示全了就好
ax.set_extent([-180, 180, 5, 90], crs=ccrs.PlateCarree())
# 收集所有省份的边界线段（格式：[(x1,y1), (x2,y2), ...]）
segments = []
for lons, lats in province_coords.values():
    # 将经纬度组合为线段的点坐标（shape: (n_points, 2)）
    segment = np.column_stack([lons, lats])
    segments.append(segment)
# 用 LineCollection 批量绘制所有线段， 之前使用过ax.plot太慢了 在我自己的电脑上运行一次得20秒 现在最多七秒多
lc = LineCollection(
    segments,
    color='red',
    linewidth=0.5,
    transform=ccrs.PlateCarree(),  # 使用原始坐标系
    zorder=3
)
ax.add_collection(lc)

plt.show()
