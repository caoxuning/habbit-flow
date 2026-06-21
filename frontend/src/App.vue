<template>
  <section v-if="!token" class="auth-shell">
    <div class="auth-panel">
      <div>
        <p class="eyebrow">HabitFlow</p>
        <h1>自律目标追踪平台</h1>
        <p class="auth-copy">管理目标、记录每日打卡、查看成长趋势，并在连续坚持中获得勋章。</p>
      </div>
      <el-tabs v-model="authMode" stretch>
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>
      <el-form :model="authForm" label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="authForm.username" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="authForm.password" type="password" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item v-if="authMode === 'register'" label="邮箱">
          <el-input v-model="authForm.email" />
        </el-form-item>
        <el-button type="primary" class="full-button" :loading="authLoading" @click="submitAuth">
          {{ authMode === 'login' ? '登录' : '注册并登录' }}
        </el-button>
      </el-form>
    </div>
  </section>

  <section v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">HF</span>
        <div>
          <strong>HabitFlow</strong>
          <small>{{ profile?.username }}</small>
        </div>
      </div>
      <el-menu :default-active="activeView" @select="activeView = $event">
        <el-menu-item index="dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="goals">
          <el-icon><Aim /></el-icon>
          <span>目标管理</span>
        </el-menu-item>
        <el-menu-item index="checkins">
          <el-icon><Calendar /></el-icon>
          <span>打卡记录</span>
        </el-menu-item>
        <el-menu-item index="timeline">
          <el-icon><Timer /></el-icon>
          <span>成长日志</span>
        </el-menu-item>
        <el-menu-item index="badges">
          <el-icon><Medal /></el-icon>
          <span>勋章奖励</span>
        </el-menu-item>
        <el-menu-item index="profile">
          <el-icon><User /></el-icon>
          <span>个人信息</span>
        </el-menu-item>
      </el-menu>
      <el-button class="logout" :icon="SwitchButton" @click="logout">退出登录</el-button>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <h2>{{ viewTitle }}</h2>
          <p>{{ viewSubtitle }}</p>
        </div>
        <div class="top-actions">
          <el-button v-if="activeView === 'checkins'" :icon="Download" @click="exportCheckIns">导出打卡记录</el-button>
          <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="openGoalDialog()">新建目标</el-button>
        </div>
      </header>

      <div v-if="activeView === 'dashboard'" class="dashboard">
        <div class="metric-grid">
          <div v-for="item in metrics" :key="item.label" class="metric-card">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="chart-grid">
          <section class="panel">
            <div class="panel-head">
              <h3>月度成长报表</h3>
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div ref="monthlyChartRef" class="chart"></div>
          </section>
          <section class="panel">
            <div class="panel-head">
              <h3>目标完成率</h3>
              <el-icon><Aim /></el-icon>
            </div>
            <div ref="rateChartRef" class="chart"></div>
          </section>
        </div>
        <section class="panel timeline-preview">
          <div class="panel-head">
            <h3>成长日志预览</h3>
            <el-button size="small" text @click="activeView = 'timeline'">查看全部</el-button>
          </div>
          <el-timeline v-if="timelineList.length > 0">
            <el-timeline-item
              v-for="item in timelineList.slice(0, 7)"
              :key="item.date"
              :timestamp="item.date"
              placement="top"
            >
              <div v-for="evt in item.events" :key="evt.time || evt.badgeName || evt.content">
                <div v-if="evt.type === 'checkin'" style="margin-bottom: 4px;">
                  <strong>{{ evt.goalName }}</strong>
                  <p v-if="evt.remark" style="margin: 2px 0;">{{ evt.remark }}</p>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无成长记录" />
        </section>
      </div>

      <div v-if="activeView === 'goals'" class="panel">
        <el-table :data="goalRows" stripe>
          <el-table-column label="目标名称" min-width="180">
            <template #default="{ row }">
              <strong>{{ row.goal.name }}</strong>
              <small class="muted-line">{{ row.goal.type }}</small>
            </template>
          </el-table-column>
          <el-table-column prop="goal.cycle" label="周期" width="110">
            <template #default="{ row }">{{ cycleLabel(row.goal.cycle) }}</template>
          </el-table-column>
          <el-table-column label="日期" min-width="180">
            <template #default="{ row }">{{ row.goal.startDate }} 至 {{ row.goal.endDate }}</template>
          </el-table-column>
          <el-table-column label="完成率" width="180">
            <template #default="{ row }">
              <el-progress :percentage="row.completionRate" />
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.goal.status === 'ACTIVE' ? 'success' : 'info'">{{ statusLabel(row.goal.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="230" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" :icon="Check" @click="quickCheckIn(row.goal)">打卡</el-button>
              <el-button size="small" :icon="Edit" @click="openGoalDialog(row.goal)">编辑</el-button>
              <el-popconfirm title="确认删除该目标？" @confirm="deleteGoal(row.goal.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="activeView === 'checkins'" class="two-column">
        <section class="panel">
          <div class="panel-head">
            <h3>每日打卡</h3>
            <el-icon><Check /></el-icon>
          </div>
          <el-form :model="checkForm" label-position="top">
            <el-form-item label="目标">
              <el-select v-model="checkForm.goalId" class="full-button" placeholder="选择目标">
                <el-option v-for="row in goalRows" :key="row.goal.id" :label="row.goal.name" :value="row.goal.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="checkForm.remark" type="textarea" :rows="3" />
            </el-form-item>
            <el-button type="primary" :icon="Check" @click="submitCheckIn(false)">今日打卡</el-button>
          </el-form>

          <el-divider />

          <div class="panel-head compact">
            <h3>补卡申请</h3>
            <el-icon><Bell /></el-icon>
          </div>
          <el-form :model="makeupForm" label-position="top">
            <el-form-item label="目标">
              <el-select v-model="makeupForm.goalId" class="full-button" placeholder="选择目标">
                <el-option v-for="row in goalRows" :key="row.goal.id" :label="row.goal.name" :value="row.goal.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="补卡日期">
              <el-date-picker v-model="makeupForm.checkDate" value-format="YYYY-MM-DD" type="date" class="full-button" />
            </el-form-item>
            <el-form-item label="原因">
              <el-input v-model="makeupForm.remark" type="textarea" :rows="2" />
            </el-form-item>
            <el-button :icon="Calendar" @click="submitCheckIn(true)">提交补卡</el-button>
          </el-form>
        </section>

        <section class="panel">
          <div class="panel-head">
            <h3>打卡记录</h3>
            <el-icon><Calendar /></el-icon>
          </div>
          <el-table :data="checkIns" height="560" stripe>
            <el-table-column prop="checkDate" label="日期" width="120" />
            <el-table-column label="目标" min-width="140">
              <template #default="{ row }">{{ goalName(row.goalId) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="160" />
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                <el-tag :type="row.makeup ? 'warning' : 'success'">{{ row.makeup ? '补卡' : '打卡' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </div>

      <div v-if="activeView === 'timeline'" class="panel">
        <div class="panel-head">
          <h3>成长日志时间线</h3>
          <div>
            <span style="font-size: 14px; color: #909399; margin-right: 8px;">近</span>
            <el-select v-model="timelineDays" style="width: 100px;" @change="loadTimeline">
              <el-option label="7天" :value="7" />
              <el-option label="30天" :value="30" />
              <el-option label="90天" :value="90" />
              <el-option label="全部" :value="0" />
            </el-select>
          </div>
        </div>
        <el-timeline v-if="timelineList.length > 0">
          <el-timeline-item
            v-for="item in timelineList"
            :key="item.date"
            :timestamp="item.date"
            placement="top"
          >
            <div v-for="evt in item.events" :key="evt.time || evt.badgeName || evt.content">
              <div v-if="evt.type === 'checkin'" style="margin-bottom: 8px;">
                <strong>{{ evt.goalName }}</strong>
                <p v-if="evt.remark" style="margin: 4px 0;">{{ evt.remark }}</p>
                <el-tag v-if="evt.makeup" size="small" type="warning">补卡</el-tag>
              </div>
              <div v-else-if="evt.type === 'badge'" style="margin-bottom: 8px;">
                <el-tag type="success" size="small">🏅 {{ evt.badgeName }}</el-tag>
                <small style="color: #909399; margin-left: 6px;">{{ evt.badgeDescription }}</small>
              </div>
              <div v-else-if="evt.type === 'inspiration'" style="margin-bottom: 8px; padding: 8px; background: #f5f7fa; border-radius: 6px;">
                <small style="color: #909399;">💡 推荐</small>
                <p style="margin: 4px 0;">{{ evt.content }}</p>
                <small v-if="evt.cn" style="color: #909399;">{{ evt.cn }}</small>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无成长记录" />
      </div>

      <div v-if="activeView === 'badges'" class="badge-grid">
        <article v-for="badge in badges" :key="badge.id" class="badge-card">
          <div class="badge-icon"><el-icon><Medal /></el-icon></div>
          <strong>{{ badge.name }}</strong>
          <p>{{ badge.description }}</p>
          <small>{{ badge.conditionText }}</small>
        </article>
        <el-empty v-if="badges.length === 0" description="完成首次打卡即可获得第一枚勋章" />
      </div>

      <div v-if="activeView === 'profile'" class="two-column narrow">
        <section class="panel">
          <div class="panel-head">
            <h3>个人信息维护</h3>
            <el-icon><User /></el-icon>
          </div>
          <el-form :model="profileForm" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-button type="primary" @click="saveProfile">保存资料</el-button>
          </el-form>
        </section>
        <section class="panel">
          <div class="panel-head">
            <h3>修改密码</h3>
            <el-icon><Lock /></el-icon>
          </div>
          <el-form :model="passwordForm" label-position="top">
            <el-form-item label="原密码">
              <el-input v-model="passwordForm.oldPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" show-password />
            </el-form-item>
            <el-button @click="changePassword">更新密码</el-button>
          </el-form>
        </section>
      </div>
    </main>

    <el-dialog v-model="goalDialogVisible" :title="goalForm.id ? '编辑目标' : '新建目标'" width="520px">
      <el-form :model="goalForm" label-position="top">
        <el-form-item label="目标名称">
          <el-input v-model="goalForm.name" placeholder="每天运动30分钟" />
        </el-form-item>
        <el-form-item label="目标类型">
          <el-input v-model="goalForm.type" placeholder="运动、学习、阅读" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="开始日期">
            <el-date-picker v-model="goalForm.startDate" value-format="YYYY-MM-DD" type="date" class="full-button" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="goalForm.endDate" value-format="YYYY-MM-DD" type="date" class="full-button" />
          </el-form-item>
        </div>
        <div class="form-grid">
          <el-form-item label="目标周期">
            <el-select v-model="goalForm.cycle" class="full-button">
              <el-option label="每日" value="DAILY" />
              <el-option label="每周" value="WEEKLY" />
              <el-option label="每月" value="MONTHLY" />
            </el-select>
          </el-form-item>
          <el-form-item label="每日目标次数">
            <el-input-number v-model="goalForm.dailyTargetCount" :min="1" class="full-button" />
          </el-form-item>
        </div>
        <el-form-item label="状态">
          <el-segmented v-model="goalForm.status" :options="statusOptions" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="goalDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveGoal">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Aim, Bell, Calendar, Check, DataAnalysis, Download, Edit, Lock, Medal, Plus, Refresh, SwitchButton, Timer, User } from '@element-plus/icons-vue'
import { authApi, badgeApi, checkInApi, exportApi, goalApi, statsApi, userApi } from './api'

const token = ref(localStorage.getItem('habitflow_token'))
const profile = ref(JSON.parse(localStorage.getItem('habitflow_profile') || 'null'))
const authMode = ref('login')
const authLoading = ref(false)
const activeView = ref('dashboard')
const authForm = reactive({ username: '', password: '', email: '' })
const dashboard = ref(null)
const goalRows = ref([])
const checkIns = ref([])
const badges = ref([])
const monthlyChartRef = ref()
const rateChartRef = ref()
let monthlyChart
let rateChart

const goalDialogVisible = ref(false)
const goalForm = reactive(emptyGoal())
const checkForm = reactive({ goalId: null, remark: '' })
const makeupForm = reactive({ goalId: null, checkDate: '', remark: '' })
const timelineList = ref([])
const timelineDays = ref(30)
const profileForm = reactive({ username: '', email: '' })
const passwordForm = reactive({ oldPassword: '', newPassword: '' })
const statusOptions = [
  { label: '进行中', value: 'ACTIVE' },
  { label: '已暂停', value: 'PAUSED' },
  { label: '已完成', value: 'DONE' }
]

const viewTitle = computed(() => ({
  dashboard: '数据概览',
  goals: '目标管理',
  checkins: '打卡管理',
  timeline: '成长日志',
  badges: '勋章奖励',
  profile: '个人中心'
}[activeView.value]))

const viewSubtitle = computed(() => ({
  dashboard: '查看完成次数、连续打卡、完成率与月度成长趋势。',
  goals: '创建目标、设置周期、维护每日目标次数。',
  checkins: '提交每日打卡，处理历史补卡并查看记录。',
  timeline: '按时间线回顾你的每一次坚持与成长。',
  badges: '系统根据坚持情况自动发放奖励。',
  profile: '维护账号资料并定期更新密码。'
}[activeView.value]))

const metrics = computed(() => [
  { label: '目标总数', value: dashboard.value?.totalGoals ?? 0 },
  { label: '进行中目标', value: dashboard.value?.activeGoals ?? 0 },
  { label: '总完成次数', value: dashboard.value?.totalCheckIns ?? 0 },
  { label: '连续打卡天数', value: dashboard.value?.currentStreakDays ?? 0 },
  { label: '平均完成率', value: `${dashboard.value?.averageCompletionRate ?? 0}%` }
])

onMounted(() => {
  if (token.value) {
    loadAll()
  }
})

watch(activeView, () => {
  if (activeView.value === 'dashboard') {
    nextTick(renderCharts)
  }
  if (activeView.value === 'timeline') {
    loadTimeline()
  }
})

async function submitAuth() {
  authLoading.value = true
  try {
    const data = authMode.value === 'login'
      ? await authApi.login(authForm)
      : await authApi.register(authForm)
    token.value = data.token
    profile.value = data.profile
    localStorage.setItem('habitflow_token', data.token)
    localStorage.setItem('habitflow_profile', JSON.stringify(data.profile))
    Object.assign(profileForm, { username: data.profile.username, email: data.profile.email })
    await loadAll()
    ElMessage.success('登录成功')
  } finally {
    authLoading.value = false
  }
}

async function loadAll() {
  if (!token.value) return
  const [profileData, statsData, goalsData, checksData, badgeData, timelineData] = await Promise.all([
    userApi.profile(),
    statsApi.dashboard(),
    goalApi.list(),
    checkInApi.list(),
    badgeApi.mine(),
    statsApi.timeline(timelineDays.value)
  ])
  profile.value = profileData
  localStorage.setItem('habitflow_profile', JSON.stringify(profileData))
  Object.assign(profileForm, { username: profileData.username, email: profileData.email })
  dashboard.value = statsData
  goalRows.value = goalsData
  checkIns.value = checksData
  badges.value = badgeData
  timelineList.value = timelineData
  await nextTick()
  renderCharts()
}

function renderCharts() {
  if (!monthlyChartRef.value || !rateChartRef.value) return
  monthlyChart = monthlyChart || echarts.init(monthlyChartRef.value)
  rateChart = rateChart || echarts.init(rateChartRef.value)
  monthlyChart.setOption({
    tooltip: {},
    grid: { top: 28, left: 38, right: 16, bottom: 32 },
    xAxis: { type: 'category', data: dashboard.value?.monthlyReport?.map((item) => item.month) || [] },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: dashboard.value?.monthlyReport?.map((item) => item.count) || [], itemStyle: { color: '#2f80ed' } }]
  })
  rateChart.setOption({
    tooltip: {},
    grid: { top: 28, left: 38, right: 16, bottom: 48 },
    xAxis: { type: 'category', data: goalRows.value.map((item) => item.goal.name), axisLabel: { interval: 0, rotate: 25 } },
    yAxis: { type: 'value', max: 100 },
    series: [{ type: 'line', smooth: true, data: goalRows.value.map((item) => item.completionRate), areaStyle: {}, itemStyle: { color: '#13a46f' } }]
  })
}

function openGoalDialog(goal) {
  Object.assign(goalForm, goal ? { ...goal } : emptyGoal())
  goalDialogVisible.value = true
}

async function saveGoal() {
  const payload = { ...goalForm }
  if (goalForm.id) {
    await goalApi.update(goalForm.id, payload)
  } else {
    await goalApi.create(payload)
  }
  goalDialogVisible.value = false
  ElMessage.success('目标已保存')
  await loadAll()
}

async function deleteGoal(id) {
  await goalApi.remove(id)
  ElMessage.success('目标已删除')
  await loadAll()
}

function showInspiration(data) {
  if (data?.inspiration) {
    const ins = data.inspiration
    let msg = `<div style="margin-bottom: 12px;"><strong>${ins.content}</strong></div>`
    if (ins.cn) msg += `<div style="color: #909399; margin-bottom: 12px;">${ins.cn}</div>`
    if (ins.example) msg += `<div style="color: #606266; font-style: italic; margin-bottom: 12px;">例句：${ins.example}</div>`
    if (data.peerTips?.length > 0) {
      msg += `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ebeef5;"><strong>同路人寄语：</strong></div>`
      data.peerTips.forEach(t => {
        msg += `<div style="margin-top: 6px; color: #606266;">「${t.remark}」<br><small style="color: #909399;">—— ${t.goalName}</small></div>`
      })
    }
    ElMessageBox.alert(msg, '🎉 打卡成功 · 精选内容', { dangerouslyUseHTMLString: true, confirmButtonText: '继续努力' })
  } else {
    ElMessage.success('打卡成功')
  }
}

async function quickCheckIn(goal) {
  const data = await checkInApi.create({ goalId: goal.id, remark: '快速打卡' })
  showInspiration(data)
  await loadAll()
}

async function submitCheckIn(isMakeup) {
  const form = isMakeup ? makeupForm : checkForm
  let data
  if (isMakeup) {
    data = await checkInApi.makeup(form)
  } else {
    data = await checkInApi.create(form)
  }
  showInspiration(data)
  Object.assign(form, isMakeup ? { goalId: null, checkDate: '', remark: '' } : { goalId: null, remark: '' })
  await loadAll()
}

async function saveProfile() {
  const data = await userApi.updateProfile(profileForm)
  profile.value = data
  localStorage.setItem('habitflow_profile', JSON.stringify(data))
  ElMessage.success('资料已更新')
}

async function changePassword() {
  await userApi.changePassword(passwordForm)
  Object.assign(passwordForm, { oldPassword: '', newPassword: '' })
  ElMessage.success('密码已更新')
}

function logout() {
  localStorage.removeItem('habitflow_token')
  localStorage.removeItem('habitflow_profile')
  token.value = ''
  profile.value = null
}

async function loadTimeline() {
  try {
    timelineList.value = await statsApi.timeline(timelineDays.value)
  } catch {
    timelineList.value = []
  }
}

async function exportCheckIns() {
  try {
    const blob = await exportApi.checkins({ format: 'xlsx' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `打卡记录_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  }
}

function goalName(id) {
  return goalRows.value.find((item) => item.goal.id === id)?.goal.name || `目标 ${id}`
}

function cycleLabel(cycle) {
  return { DAILY: '每日', WEEKLY: '每周', MONTHLY: '每月' }[cycle] || cycle
}

function statusLabel(status) {
  return { ACTIVE: '进行中', PAUSED: '已暂停', DONE: '已完成' }[status] || status
}

function emptyGoal() {
  const today = new Date()
  const end = new Date()
  end.setMonth(end.getMonth() + 1)
  return {
    id: null,
    name: '',
    type: '',
    startDate: today.toISOString().slice(0, 10),
    endDate: end.toISOString().slice(0, 10),
    cycle: 'DAILY',
    dailyTargetCount: 1,
    status: 'ACTIVE'
  }
}
</script>
