# 全屏布局修复说明文档

## 文件路径
`CodeExplanation/Full_Screen_Layout_Fix.md`

## 修复目标
解决Agent页面中图片和图谱显示区域被底部栏遮挡的问题，让聊天框、图谱和图片都能充分利用屏幕空间。

## 主要问题
1. **底部Footer遮挡内容**：App.tsx中的Footer组件在Agent页面会遮挡图片显示区域
2. **高度计算不合理**：各组件的高度设置导致内容无法充分展示
3. **空间利用不充分**：右侧面板的图片和图谱没有合理的高度分配

## 解决方案

### 1. App.tsx 修改 - 条件性显示导航栏和Footer

**修改内容**：
- 引入 `useLocation` hook 来检测当前路由
- 创建 `AppContent` 内部组件来处理条件渲染
- Agent页面不显示 `Navbar` 和 `Footer`
- Agent页面使用固定的100vh高度和overflow:hidden

**关键代码**：
```tsx
function AppContent() {
  const location = useLocation();
  const isAgentPage = location.pathname === '/agent';

  return (
    <Box sx={{
      height: isAgentPage ? '100vh' : 'auto',
      overflow: isAgentPage ? 'hidden' : 'auto',
    }}>
      {!isAgentPage && <Navbar />}
      <Box sx={{ flex: 1, height: isAgentPage ? '100%' : 'auto' }}>
        <Routes>...</Routes>
      </Box>
      {!isAgentPage && <Footer />}
    </Box>
  );
}
```

### 2. Agent.tsx 布局优化

**主要修改**：

#### 2.1 根容器优化
```tsx
// 从 minHeight: '100vh' 改为 height: '100vh'
// 添加 display: 'flex', flexDirection: 'column'
<Box sx={{
  height: '100vh', // 固定视口高度
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}}>
```

#### 2.2 Container容器优化
```tsx
// 使用 flex: 1 替代固定高度
<Container sx={{
  flex: 1, // 占满剩余空间
  height: '100%',
  overflow: 'hidden',
}}>
```

#### 2.3 主聊天区域优化
```tsx
// 移除固定高度计算，使用flex布局
<Box sx={{
  flex: 1,
  minHeight: 0, // 允许收缩
  // 移除了 height: 'calc(100vh - 80px)'
}}>
```

#### 2.4 右侧面板高度分配优化
```tsx
// 知识图谱面板：50% 高度
flex: showImagePanel ? '0 0 50%' : '1 1 100%',
minHeight: showImagePanel ? '300px' : '400px',

// 图片面板：50% 高度  
flex: showKnowledgeGraph ? '0 0 50%' : '1 1 100%',
minHeight: '200px',
```

### 3. ImageViewer.tsx 优化

**修改内容**：
- 减少图片标题占用的空间：从30px减少到25px
- 确保图片能够充分利用可用高度

```tsx
maxHeight: 'calc(100% - 25px)', // 进一步减少标题占用的空间
```

### 4. KnowledgeGraphViewer.tsx 优化

**修改内容**：
- 优化ECharts图例布局：水平排列，居中显示
- 减少图例占用空间：更小的字体和间距
- 优化力引导布局参数：更紧凑的节点排列

```tsx
legend: [{
  orient: 'horizontal', // 水平排列图例
  left: 'center', // 居中显示
  fontSize: 10, // 更小字体
  top: 2, // 减少顶部距离
}],

force: {
  repulsion: 80, // 减小斥力
  edgeLength: [40, 60], // 更短边长
  gravity: 0.3 // 增加向心力
}
```

## 技术要点

### 1. Flexbox布局策略
- 使用 `flex: 1` 让组件占满可用空间
- 使用 `minHeight: 0` 允许flex子项收缩
- 使用 `flexShrink: 0` 防止关键组件收缩

### 2. 高度管理
- 根容器使用 `height: '100vh'` 固定视口高度
- 子容器使用 `height: '100%'` 继承父容器高度
- 避免使用 `calc()` 进行复杂的高度计算

### 3. 溢出控制
- 根容器设置 `overflow: 'hidden'` 防止页面滚动
- 内容区域设置 `overflow: 'auto'` 允许内部滚动

### 4. 条件渲染
- 使用 `useLocation` hook 检测路由
- 根据页面类型条件性显示/隐藏组件

## 效果预期

修复后的布局应该实现：

1. **无底部遮挡**：Agent页面不显示Footer，图片可以延伸到屏幕底部
2. **充分利用空间**：聊天框、图谱、图片都能使用完整的可用高度
3. **合理的比例分配**：知识图谱和图片各占50%的右侧面板高度
4. **响应式适配**：在不同屏幕尺寸下都能正常显示
5. **流畅的用户体验**：无意外的滚动条，内容区域清晰可见

## 注意事项

1. **路由依赖**：修改依赖于React Router的useLocation hook
2. **样式继承**：确保所有子组件正确继承父容器的高度设置
3. **浏览器兼容性**：flexbox和100vh在所有现代浏览器中都有良好支持
4. **性能考虑**：避免不必要的重新渲染，使用合适的依赖数组

## 测试建议

1. 在不同屏幕尺寸下测试布局
2. 测试图片和图谱的显示效果
3. 验证聊天记录的滚动行为
4. 确认在Home页面Footer正常显示
5. 测试页面切换时的布局变化 