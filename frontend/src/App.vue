<template>
  <section v-if="!token" class="auth-shell">
    <canvas ref="authParticleCanvasRef" class="auth-particle-canvas" aria-hidden="true"></canvas>
    <div class="auth-stage">
      <div class="auth-panel">
        <div class="auth-heading">
          <p class="eyebrow">HabitFlow</p>
          <h1>自律目标追踪平台</h1>
          <p class="auth-copy">管理目标、记录每日打卡、查看成长趋势，并在连续坚持中获得勋章。</p>
        </div>
        <el-tabs v-model="authMode" stretch>
          <el-tab-pane label="登录" name="login" />
          <el-tab-pane label="注册" name="register" />
        </el-tabs>
        <el-form ref="authFormRef" :model="authForm" :rules="authRules" label-position="top" @submit.prevent>
          <el-form-item label="用户名" prop="username">
            <el-input v-model="authForm.username" :prefix-icon="User" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="authForm.password" type="password" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item v-if="authMode === 'register'" label="邮箱" prop="email">
            <el-input v-model="authForm.email" />
          </el-form-item>
          <el-button type="primary" class="full-button auth-submit" :loading="authLoading" @click="submitAuth">
            {{ authMode === 'login' ? '登录' : '注册并登录' }}
          </el-button>
        </el-form>
      </div>

      <aside class="auth-reveal-panel">
        <div class="auth-reveal-head">
          <span>HabitFlow Services</span>
          <p>把每天的运动、英语和同伴监督放进一个可持续的节奏里。</p>
        </div>
        <div class="reveal-list">
          <article v-for="item in authRevealItems" :key="item.text" class="reveal-item">
            <h2>{{ item.text }}</h2>
            <div class="reveal-image reveal-image-back">
              <img :src="item.images[1].src" :alt="item.images[1].alt" />
            </div>
            <div class="reveal-image reveal-image-front">
              <img :src="item.images[0].src" :alt="item.images[0].alt" />
            </div>
          </article>
        </div>
      </aside>
    </div>
  </section>

  <section v-else class="app-shell top-nav-shell">
    <header class="app-navbar">
      <div class="app-nav-inner">
        <button class="nav-brand spot-nav-button" type="button" @pointermove="updateNavSpot" @click="selectView('dashboard')">
          <span class="brand-mark">HF</span>
          <span>
            <strong>HabitFlow</strong>
            <small>{{ profile?.username }}</small>
          </span>
        </button>

        <nav class="nav-menu" aria-label="主导航">
          <button
            class="nav-link spot-nav-button"
            :class="{ active: activeView === 'dashboard' }"
            type="button"
            @pointermove="updateNavSpot"
            @click="selectView('dashboard')"
          >
            <span>工作台</span>
          </button>
          <template v-for="group in navGroups" :key="group.title">
            <button
              v-if="group.items.length === 1"
              class="nav-link spot-nav-button"
              :class="{ active: group.items[0].view === activeView }"
              type="button"
              @pointermove="updateNavSpot"
              @click="selectView(group.items[0].view)"
            >
              <span>{{ group.title }}</span>
            </button>
            <el-dropdown v-else trigger="hover" popper-class="nav-dropdown">
              <button class="nav-link spot-nav-button" :class="{ active: group.items.some((item) => item.view === activeView) }" type="button" @pointermove="updateNavSpot">
                <span>{{ group.title }}</span>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="item in group.items"
                    :key="item.view"
                    @click="selectView(item.view)"
                  >
                    <div class="nav-dropdown-item">
                      <strong>{{ item.title }}</strong>
                      <small>{{ item.description }}</small>
                    </div>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </nav>

        <div class="nav-actions">
          <span class="nav-stat">{{ activeGoalRows.length }} 个进行中目标</span>
          <button class="nav-stat nav-stat-button spot-nav-button" type="button" @pointermove="updateNavSpot" @click="selectView('notifications')">
            <span>{{ notificationUnreadCount }} 条未读提醒</span>
          </button>
          <el-badge v-if="notificationUnreadCount > 0" :value="notificationUnreadCount">
            <el-button :icon="Bell" circle @click="selectView('notifications')" />
          </el-badge>
          <el-button :icon="Refresh" circle @click="loadAll" />
          <el-button class="desktop-only" :icon="SwitchButton" @click="logout">退出</el-button>
          <button class="mobile-menu-button spot-nav-button" type="button" aria-label="打开菜单" @pointermove="updateNavSpot" @click="mobileNavOpen = true"><span>☰</span></button>
        </div>
      </div>

      <transition name="mobile-nav-fade">
        <div v-if="mobileNavOpen" class="mobile-nav-layer" @click.self="mobileNavOpen = false">
          <aside class="mobile-nav-panel">
            <div class="mobile-nav-head">
              <div class="nav-brand compact">
                <span class="brand-mark">HF</span>
                <span>
                  <strong>HabitFlow</strong>
                  <small>{{ profile?.username }}</small>
                </span>
              </div>
              <button type="button" class="mobile-nav-close spot-nav-button" @pointermove="updateNavSpot" @click="mobileNavOpen = false"><span>x</span></button>
            </div>
            <button class="mobile-nav-link spot-nav-button" type="button" @pointermove="updateNavSpot" @click="selectView('dashboard')"><span>工作台</span></button>
            <section v-for="group in navGroups" :key="group.title" class="mobile-nav-group">
              <strong>{{ group.title }}</strong>
              <button
                v-for="item in group.items"
                :key="item.view"
                class="mobile-nav-link spot-nav-button"
                type="button"
                @pointermove="updateNavSpot"
                @click="selectView(item.view)"
              >
                <span>{{ item.title }}</span>
                <small>{{ item.description }}</small>
              </button>
            </section>
            <el-button class="full-button" :icon="SwitchButton" @click="logout">退出登录</el-button>
          </aside>
        </div>
      </transition>
    </header>

    <main class="workspace">
      <div v-if="activeView === 'dashboard'" class="dashboard dashboard-workspace">
        <aside class="dashboard-side-panel panel">
          <div class="dashboard-side-head">
            <span>今日工作台</span>
            <h3>{{ greetingText }}，{{ profile?.username || 'HabitFlow 用户' }}</h3>
            <p>{{ todayFocusText }}</p>
          </div>
          <div class="focus-meter dashboard-meter" :style="{ '--focus-progress': todayProgressStyle }">
            <strong>{{ todayProgress }}%</strong>
            <span>今日完成</span>
          </div>
          <div class="dashboard-side-stats">
            <article>
              <strong>{{ todayDoneCount }}/{{ todayGoals.length }}</strong>
              <span>今日打卡</span>
            </article>
            <article>
              <strong>{{ dashboard?.currentStreakDays ?? 0 }}</strong>
              <span>连续天数</span>
            </article>
            <article>
              <strong>{{ dashboard?.totalCheckIns ?? 0 }}</strong>
              <span>累计打卡</span>
            </article>
          </div>
          <div class="dashboard-action-list compact">
            <button type="button" class="spot-nav-button" @pointermove="updateNavSpot" @click="activeView = 'checkins'">
              <strong>快速打卡</strong>
              <span>提交今日记录</span>
            </button>
            <button type="button" class="spot-nav-button" @pointermove="updateNavSpot" @click="activeView = 'calendar'">
              <strong>任务日历</strong>
              <span>查看今日安排</span>
            </button>
            <button type="button" class="spot-nav-button" @pointermove="updateNavSpot" @click="activeView = 'social'">
              <strong>好友监督</strong>
              <span>查看同伴进展</span>
            </button>
          </div>
        </aside>

        <section class="dashboard-main">
          <section class="panel dashboard-today-card">
            <div class="panel-head">
              <div>
                <h3>今日打卡</h3>
                <p class="panel-copy">按今天的目标查看完成情况。</p>
              </div>
              <el-button size="small" type="primary" :icon="Check" @click="activeView = 'checkins'">去打卡</el-button>
            </div>
            <div class="dashboard-task-list">
              <article
                v-for="item in todayGoals"
                :key="item.goal.id"
                class="dashboard-task-row"
                :class="[priorityClass(item.goal.priority), { done: checkInForGoalDate(item.goal.id, new Date().toISOString().slice(0, 10)) }]"
              >
                <div>
                  <strong>{{ item.goal.name }}</strong>
                  <span>{{ item.goal.type }} · {{ cycleLabel(item.goal.cycle) }} · {{ priorityLabel(item.goal.priority) }}</span>
                </div>
                <el-tag :type="checkInForGoalDate(item.goal.id, new Date().toISOString().slice(0, 10)) ? 'success' : 'warning'">
                  {{ checkInForGoalDate(item.goal.id, new Date().toISOString().slice(0, 10)) ? '已打卡' : '待打卡' }}
                </el-tag>
                <el-button size="small" :disabled="!!checkInForGoalDate(item.goal.id, new Date().toISOString().slice(0, 10))" @click="quickCheckIn(item.goal)">
                  打卡
                </el-button>
              </article>
              <el-empty v-if="todayGoals.length === 0" description="今天暂无目标" />
            </div>
          </section>

          <section class="panel dashboard-rank-card">
            <div class="panel-head">
              <div>
                <h3>打卡排行榜</h3>
                <p class="panel-copy">好友和圈子的累计打卡排名。</p>
              </div>
              <el-button size="small" text @click="activeView = 'social'; socialTab = 'leaderboard'">查看全部</el-button>
            </div>
            <div class="dashboard-rank-grid">
              <div class="dashboard-rank-section">
                <span class="dashboard-section-label">好友</span>
                <article v-for="item in friendLeaderboard.slice(0, 4)" :key="item.user.id" class="dashboard-rank-row" :class="{ mine: item.isMe }">
                  <span>{{ item.rank }}</span>
                  <strong>{{ item.user.username }}</strong>
                  <small>{{ item.checkInCount }} 次</small>
                </article>
                <el-empty v-if="friendLeaderboard.length === 0" description="暂无好友排行" />
              </div>
              <div class="dashboard-rank-section">
                <span class="dashboard-section-label">圈子</span>
                <article v-for="item in circleLeaderboard.slice(0, 4)" :key="item.circle.id" class="dashboard-rank-row">
                  <span>{{ item.rank }}</span>
                  <strong>{{ item.circle.name }}</strong>
                  <small>{{ item.checkInCount }} 次</small>
                </article>
                <el-empty v-if="circleLeaderboard.length === 0" description="暂无圈子排行" />
              </div>
            </div>
          </section>

          <section class="panel dashboard-activity-card">
            <div class="panel-head">
              <div>
                <h3>最近打卡</h3>
                <p class="panel-copy">查看最近完成的目标记录。</p>
              </div>
              <el-button size="small" text @click="activeView = 'timeline'">成长日志</el-button>
            </div>
            <div class="dashboard-activity-list">
              <article v-for="item in checkIns.slice(0, 8)" :key="item.id" class="dashboard-activity-row">
                <div>
                  <strong>{{ item.goalName || goalName(item.goalId) }}</strong>
                  <span>{{ item.checkDate }} · {{ item.remark || '已完成打卡' }}</span>
                </div>
                <el-tag size="small" :type="item.makeup ? 'warning' : 'success'">{{ item.makeup ? '补卡' : '打卡' }}</el-tag>
              </article>
              <el-empty v-if="checkIns.length === 0" description="暂无打卡记录" />
            </div>
          </section>
        </section>
      </div>

      <div v-if="activeView === 'calendar'" class="calendar-layout">
        <section class="panel calendar-panel">
          <div class="panel-head calendar-head">
            <div>
              <h3>任务日历</h3>
              <p>每天只展示一个紧急目标和一个其他目标，点击日期查看完整日程和打卡状态。</p>
            </div>
            <div class="priority-legend">
              <span><i class="priority-dot priority-normal"></i>普通</span>
              <span><i class="priority-dot priority-important"></i>重要</span>
              <span><i class="priority-dot priority-urgent"></i>紧急</span>
            </div>
          </div>
          <el-calendar v-model="calendarDate">
            <template #date-cell="{ data }">
              <div
                class="calendar-cell"
                role="button"
                tabindex="0"
                @click="openCalendarDay(data.day)"
                @keydown.enter.prevent="openCalendarDay(data.day)"
                @keydown.space.prevent="openCalendarDay(data.day)"
              >
                <strong class="calendar-day">{{ dayNumber(data.day) }}</strong>
                <div class="calendar-task-list">
                  <article
                    v-for="item in calendarSummaryForDate(data.day)"
                    :key="`${data.day}-${item.key}`"
                    class="calendar-task"
                    :class="priorityClass(item.priority)"
                  >
                    <span>{{ item.title }}</span>
                    <small>{{ item.label }}{{ item.count > 1 ? ` +${item.count - 1}` : '' }}</small>
                  </article>
                </div>
                <div v-if="calendarOverflowCount(data.day) > 0" class="calendar-overflow-hint">
                  <span>...</span>
                  <small>共 {{ calendarOverflowCount(data.day) }} 项目标</small>
                </div>
              </div>
            </template>
          </el-calendar>
        </section>

        <section class="panel calendar-side">
          <div class="panel-head">
            <h3>今日任务</h3>
            <el-icon><Calendar /></el-icon>
          </div>
          <article v-for="item in todayGoals" :key="item.goal.id" class="today-task" :class="priorityClass(item.goal.priority)">
            <div>
              <strong>{{ item.goal.name }}</strong>
              <span>{{ item.goal.type }} · {{ cycleLabel(item.goal.cycle) }}</span>
            </div>
            <el-button size="small" type="primary" :icon="Check" @click="quickCheckIn(item.goal)">打卡</el-button>
          </article>
          <el-empty v-if="todayGoals.length === 0" description="今天暂无目标" />
        </section>
      </div>

      <div v-if="activeView === 'goals'" class="panel">
        <div class="panel-head">
          <div>
            <h3>目标管理</h3>
            <p class="panel-copy">在这里新建目标、设置周期和重要程度，保存后会自动出现在任务日历中。</p>
          </div>
          <el-button type="primary" :icon="Plus" @click="openGoalDialog()">新建目标</el-button>
        </div>
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
          <el-table-column label="重要程度" width="110">
            <template #default="{ row }">
              <el-tag :type="priorityTagType(row.goal.priority)">{{ priorityLabel(row.goal.priority) }}</el-tag>
            </template>
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
              <el-tooltip :disabled="row.goal.status === 'ACTIVE'" content="只有进行中的目标可以打卡">
                <span>
                  <el-button size="small" type="primary" :icon="Check" :disabled="row.goal.status !== 'ACTIVE'" @click="quickCheckIn(row.goal)">打卡</el-button>
                </span>
              </el-tooltip>
              <el-button size="small" :icon="Edit" @click="openGoalDialog(row.goal)">编辑</el-button>
              <el-popconfirm title="确认归档该目标？历史打卡记录会保留。" @confirm="deleteGoal(row.goal.id)">
                <template #reference>
                  <el-button size="small" type="danger">归档</el-button>
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
                <el-option v-for="row in activeGoalRows" :key="row.goal.id" :label="row.goal.name" :value="row.goal.id" />
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
                <el-option v-for="row in activeGoalRows" :key="row.goal.id" :label="row.goal.name" :value="row.goal.id" />
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
            <el-button :icon="Download" @click="exportCheckIns">导出打卡记录</el-button>
          </div>
          <div class="record-tools">
            <el-select v-model="recordFilters.goalId" clearable placeholder="全部目标" @change="loadCheckIns">
              <el-option v-for="row in goalRows" :key="row.goal.id" :label="row.goal.name" :value="row.goal.id" />
            </el-select>
            <el-date-picker
              v-model="recordFilters.dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="loadCheckIns"
            />
          </div>
          <el-table :data="checkIns" height="560" stripe>
            <el-table-column prop="checkDate" label="日期" width="120" />
            <el-table-column label="目标" min-width="140">
              <template #default="{ row }">{{ row.goalName || goalName(row.goalId) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="160" />
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                <el-tag :type="row.makeup ? 'warning' : 'success'">{{ row.makeup ? '补卡' : '打卡' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="打卡时间" width="170">
              <template #default="{ row }">{{ formatDateTime(row.checkTime) }}</template>
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

      <div v-if="activeView === 'notifications'" class="notification-workspace">
        <aside class="notification-side-nav" aria-label="消息提醒分类">
          <button
            v-for="tab in notificationTabs"
            :key="tab.name"
            class="social-side-link spot-nav-button"
            :class="{ active: notificationMode === tab.name }"
            type="button"
            @pointermove="updateNavSpot"
            @click="notificationMode = tab.name"
          >
            <span>{{ tab.kicker }}</span>
            <strong>{{ tab.label }}</strong>
            <small>{{ tab.description }}</small>
          </button>
        </aside>

        <section class="notification-content">
          <section class="panel notification-overview-panel">
            <div class="panel-head">
              <div>
                <h3>消息提醒</h3>
                <p class="panel-copy">集中处理今日打卡、目标到期和连续中断提醒。</p>
              </div>
              <div class="notification-actions">
                <el-switch v-model="notificationFilters.unreadOnly" active-text="只看未读" @change="loadNotifications" />
              </div>
            </div>
            <div class="notification-summary">
              <article>
                <strong>{{ notificationUnreadCount }}</strong>
                <span>未读提醒</span>
              </article>
              <article>
                <strong>{{ activeGoalRows.length }}</strong>
                <span>进行中目标</span>
              </article>
              <article>
                <strong>{{ todayDoneCount }}/{{ todayGoals.length }}</strong>
                <span>今日打卡</span>
              </article>
            </div>
          </section>

          <section class="panel notification-feed-panel">
            <div class="panel-head compact">
              <div>
                <h3>{{ currentNotificationTab.label }}</h3>
                <p class="panel-copy">{{ currentNotificationTab.description }}</p>
              </div>
              <el-tag effect="plain">{{ filteredNotifications.length }} 条</el-tag>
            </div>
            <div class="notification-list">
              <article
                v-for="item in filteredNotifications"
                :key="item.id"
                class="notification-item"
                :class="[notificationTypeClass(item.type), { unread: !item.read }]"
              >
                <div class="notification-icon">
                  <el-icon><Bell /></el-icon>
                </div>
                <div class="notification-body">
                  <div class="notification-title-row">
                    <strong>{{ item.title }}</strong>
                    <el-tag :type="notificationTagType(item.type)" effect="plain">{{ notificationTypeLabel(item.type) }}</el-tag>
                    <el-tag v-if="!item.read" type="danger" effect="dark">未读</el-tag>
                  </div>
                  <p>{{ item.content }}</p>
                  <small>{{ formatDateTime(item.createTime) }}</small>
                </div>
              </article>
              <el-empty v-if="filteredNotifications.length === 0" description="当前分类暂无提醒" />
            </div>
          </section>

          <section class="panel notification-assist-panel">
            <div class="panel-head compact">
              <div>
                <h3>今日处理建议</h3>
                <p class="panel-copy">根据目标和消息状态给出下一步动作。</p>
              </div>
              <el-icon><Timer /></el-icon>
            </div>
            <div class="notification-action-grid">
              <article v-for="item in notificationActionCards" :key="item.title">
                <span>{{ item.kicker }}</span>
                <strong>{{ item.title }}</strong>
                <small>{{ item.description }}</small>
              </article>
            </div>
          </section>
        </section>
      </div>

      <div v-if="activeView === 'badges'" class="badge-workspace">
        <aside class="badge-side-panel panel">
          <div class="badge-hero-medal"><el-icon><Medal /></el-icon></div>
          <span>自律成就</span>
          <h3>{{ badges.length }} 枚已解锁</h3>
          <p>勋章会跟随你的连续打卡、累计完成和社交互动逐步点亮。</p>
          <div class="badge-side-stats">
            <article>
              <strong>{{ dashboard?.currentStreakDays ?? 0 }}</strong>
              <span>连续天数</span>
            </article>
            <article>
              <strong>{{ dashboard?.totalCheckIns ?? 0 }}</strong>
              <span>累计打卡</span>
            </article>
            <article>
              <strong>{{ badgeProgress }}%</strong>
              <span>收藏进度</span>
            </article>
          </div>
        </aside>

        <section class="badge-content">
          <section class="panel badge-showcase-panel">
            <div class="panel-head">
              <div>
                <h3>我的勋章墙</h3>
                <p class="panel-copy">展示已经获得的成就和解锁条件。</p>
              </div>
              <el-tag type="success" effect="plain">{{ badges.length }} 已获得</el-tag>
            </div>
            <div class="badge-grid badge-grid-rich">
              <article v-for="badge in badges" :key="badge.id" class="badge-card badge-card-rich">
                <div class="badge-icon"><el-icon><Medal /></el-icon></div>
                <div>
                  <strong>{{ badge.name }}</strong>
                  <p>{{ badge.description }}</p>
                  <small>{{ badge.conditionText }}</small>
                  <small v-if="badge.obtainedTime">获得时间：{{ formatDateTime(badge.obtainedTime) }}</small>
                </div>
              </article>
              <article v-for="item in badgeRoadmap" :key="item.name" class="badge-card badge-card-rich locked">
                <div class="badge-icon"><el-icon><Lock /></el-icon></div>
                <div>
                  <strong>{{ item.name }}</strong>
                  <p>{{ item.description }}</p>
                  <small>{{ item.condition }}</small>
                </div>
              </article>
              <el-empty v-if="badges.length === 0 && badgeRoadmap.length === 0" description="完成首次打卡即可获得第一枚勋章" />
            </div>
          </section>

          <section class="panel badge-plan-panel">
            <div class="panel-head compact">
              <div>
                <h3>下一枚勋章</h3>
                <p class="panel-copy">保持今天的节奏，优先完成还没打卡的目标。</p>
              </div>
              <el-icon><Aim /></el-icon>
            </div>
            <div class="badge-plan-list">
              <article v-for="item in badgePlanCards" :key="item.title">
                <span>{{ item.kicker }}</span>
                <strong>{{ item.title }}</strong>
                <small>{{ item.description }}</small>
              </article>
            </div>
          </section>
        </section>
      </div>

      <div v-if="activeView === 'social'" class="social-space social-workspace">
        <aside class="social-side-nav" aria-label="社交模块导航">
          <button
            v-for="item in socialTabs"
            :key="item.name"
            class="social-side-link spot-nav-button"
            :class="{ active: socialTab === item.name }"
            type="button"
            @pointermove="updateNavSpot"
            @click="openSocialSection(item.name)"
          >
            <span>{{ item.kicker }}</span>
            <strong>{{ item.label }}</strong>
            <small>{{ item.description }}</small>
          </button>
        </aside>

        <section class="social-content">
        <div v-if="socialTab === 'friends'" class="friends-dashboard">
          <section class="panel social-wide friend-checkin-board">
            <div class="panel-head">
              <div>
                <h3>好友今日打卡看板</h3>
                <p class="panel-copy">查看好友今天是否完成打卡，并及时发送提醒或鼓励。</p>
              </div>
              <el-icon><Check /></el-icon>
            </div>
            <div class="friend-checkin-list">
              <article v-for="item in friendCheckinBoard" :key="item.friend.id" class="friend-checkin-card" :class="{ done: item.checkedIn }">
                <div class="avatar-sm">{{ userInitial(item.friend) }}</div>
                <div>
                  <strong>{{ item.friend.username }}</strong>
                  <span v-if="item.checkedIn">
                    已完成 {{ item.doneCount }} 次打卡，最近：{{ item.latestCheckIn?.goalName || '目标' }}
                  </span>
                  <span v-else>
                    今天还没有打卡记录，当前进行中目标 {{ item.activeGoalCount }} 个
                  </span>
                </div>
                <el-tag :type="item.checkedIn ? 'success' : 'warning'">{{ item.checkedIn ? '已打卡' : '待提醒' }}</el-tag>
                <el-button size="small" :type="item.checkedIn ? 'primary' : 'warning'" @click="sendCheckinNudge(item)">
                  {{ item.checkedIn ? '鼓励' : '提醒' }}
                </el-button>
              </article>
              <el-empty v-if="friendCheckinBoard.length === 0" description="添加好友后即可查看今日打卡状态" />
            </div>

            <div class="friend-directory-inline">
              <div class="panel-head compact">
                <div>
                  <h3>好友列表</h3>
                  <p class="panel-copy">点击聊天进入会话。</p>
                </div>
                <el-icon><User /></el-icon>
              </div>
              <div class="friend-list">
                <article v-for="friend in friends" :key="friend.id" class="friend-card">
                  <div class="avatar-sm">{{ userInitial(friend) }}</div>
                  <div>
                    <strong>{{ friend.username }}</strong>
                    <span>{{ friend.email || '未填写邮箱' }}</span>
                  </div>
                  <el-button size="small" type="primary" @click="openChat(friend)">聊天</el-button>
                </article>
                <el-empty v-if="friends.length === 0" description="搜索用户并发送好友申请" />
              </div>
            </div>
          </section>

          <section class="panel friend-search-panel">
            <div class="panel-head">
              <div>
                <h3>发现好友</h3>
                <p class="panel-copy">搜索同学账号，发送好友申请后即可聊天。</p>
              </div>
              <el-icon><User /></el-icon>
            </div>
            <div class="inline-form">
              <el-input v-model="userKeyword" placeholder="输入用户名关键词" clearable @keyup.enter="searchUsers" />
              <el-button type="primary" :icon="Refresh" @click="searchUsers">搜索</el-button>
            </div>
            <el-table class="fill-table" :data="socialUsers" height="100%" stripe>
              <el-table-column prop="username" label="用户名" min-width="130" />
              <el-table-column prop="email" label="邮箱" min-width="160" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag>{{ friendshipLabel(row.friendshipStatus) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="110">
                <template #default="{ row }">
                  <el-button size="small" type="primary" :disabled="row.friendshipStatus !== 'NONE' && row.friendshipStatus !== 'REJECTED'" @click="requestFriend(row)">
                    申请
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>

          <section class="panel friend-request-panel">
            <div class="panel-head">
              <div>
                <h3>好友申请</h3>
                <p class="panel-copy">处理收到的好友请求。</p>
              </div>
              <el-icon><Bell /></el-icon>
            </div>
            <el-table class="fill-table" :data="friendRequests" height="100%" stripe>
              <el-table-column label="申请人" min-width="120">
                <template #default="{ row }">{{ row.requester.username }}</template>
              </el-table-column>
              <el-table-column prop="message" label="留言" min-width="160" />
              <el-table-column label="状态" width="90">
                <template #default="{ row }">
                  <el-tag>{{ friendshipLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" type="success" :disabled="row.status !== 'PENDING'" @click="handleFriendRequest(row.id, true)">同意</el-button>
                  <el-button size="small" :disabled="row.status !== 'PENDING'" @click="handleFriendRequest(row.id, false)">拒绝</el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>

        </div>

        <div v-if="socialTab === 'chat'" class="chat-layout">
          <section class="chat-friends">
            <div class="chat-list-head">
              <div>
                <h3>消息</h3>
                <span>{{ friends.length }} 位好友</span>
              </div>
              <el-button text :icon="Refresh" @click="loadSocialData" />
            </div>
            <button
              v-for="friend in friends"
              :key="friend.id"
              class="chat-friend"
              :class="{ active: selectedChatFriendId === friend.id }"
              type="button"
              @click="openChat(friend)"
            >
              <div class="chat-avatar">{{ userInitial(friend) }}</div>
              <div class="chat-friend-main">
                <strong>{{ friend.username }}</strong>
                <span>{{ friend.email || '点击打开会话' }}</span>
              </div>
              <small>好友</small>
            </button>
            <el-empty v-if="friends.length === 0" description="添加好友后即可聊天" />
          </section>

          <section class="chat-panel">
            <div class="chat-thread-head">
              <div class="avatar-sm">{{ selectedChatFriend ? userInitial(selectedChatFriend) : 'H' }}</div>
              <div>
                <h3>{{ selectedChatFriend ? selectedChatFriend.username : '选择好友开始聊天' }}</h3>
                <span>{{ selectedChatFriend ? '好友 · 私信' : '从左侧选择一个会话' }}</span>
              </div>
              <el-button :icon="Refresh" :disabled="!selectedChatFriendId" @click="loadMessages(selectedChatFriendId)">刷新</el-button>
            </div>
            <div class="message-list">
              <article
                v-for="message in chatMessages"
                :key="message.id"
                class="message-row"
                :class="{ mine: message.sender.id === profile?.id }"
              >
                <div class="message-avatar">{{ message.sender.id === profile?.id ? profileInitial : userInitial(message.sender) }}</div>
                <div class="message-stack">
                  <div class="message-meta">
                    <strong>{{ message.sender.id === profile?.id ? '我' : message.sender.username }}</strong>
                    <time>{{ formatTime(message.createTime) }}</time>
                  </div>
                  <p class="message-content">{{ message.content }}</p>
                </div>
              </article>
              <el-empty v-if="selectedChatFriendId && chatMessages.length === 0" description="还没有聊天记录" />
              <el-empty v-if="!selectedChatFriendId" description="从左侧选择一个好友" />
            </div>
            <div class="message-composer">
              <el-input
                v-model="messageForm.content"
                placeholder="输入消息，按 Enter 发送"
                :disabled="!selectedChatFriendId"
                @keyup.enter="sendMessage"
              />
              <el-button type="primary" :disabled="!selectedChatFriendId" @click="sendMessage">发送</el-button>
            </div>
          </section>
        </div>

        <div v-if="socialTab === 'circles'" class="circle-workspace community-layout">
          <aside class="circle-rail">
            <div class="circle-rail-head">
              <div>
                <h3>圈子广场</h3>
                <p>{{ joinedCircles.length }} 个已加入</p>
              </div>
              <el-icon><Medal /></el-icon>
            </div>
            <div class="circle-list">
              <article v-for="circle in circles" :key="circle.id" class="circle-card" :class="{ active: selectedCircleId === circle.id }" @click="selectCircle(circle)">
                <div class="circle-icon">{{ circle.icon || 'TAG' }}</div>
                <div>
                  <strong>{{ circle.name }}</strong>
                  <span>{{ circle.description }}</span>
                </div>
                <el-button size="small" :type="circle.joined ? 'warning' : 'primary'" @click.stop="toggleCircle(circle)">
                  {{ circle.joined ? '退出' : '加入' }}
                </el-button>
                <small>{{ circle.memberCount }} 人</small>
              </article>
              <el-empty v-if="circles.length === 0" description="暂无圈子" />
            </div>

            <el-collapse class="circle-create" accordion>
              <el-collapse-item title="创建新圈子" name="create">
                <el-form :model="circleForm" label-position="top">
                  <el-form-item label="圈子名称">
                    <el-input v-model="circleForm.name" placeholder="英语打卡圈" />
                  </el-form-item>
                  <el-form-item label="圈子简介">
                    <el-input v-model="circleForm.description" type="textarea" :rows="2" />
                  </el-form-item>
                  <el-form-item label="图标标识">
                    <el-input v-model="circleForm.icon" placeholder="READ" />
                  </el-form-item>
                  <el-button class="full-button" type="primary" :icon="Plus" @click="createCircle">创建圈子</el-button>
                </el-form>
              </el-collapse-item>
            </el-collapse>
          </aside>

          <section class="panel circle-feed-panel community-feed">
            <div class="community-cover">
              <div>
                <h3>{{ selectedCircle ? selectedCircle.name : '圈子帖子' }}</h3>
                <p class="panel-copy">{{ selectedCircle?.description || '选择一个圈子查看动态。' }}</p>
              </div>
              <div class="community-cover-stats">
                <span><strong>{{ selectedCircle?.memberCount || 0 }}</strong>成员</span>
                <span><strong>{{ circlePosts.length }}</strong>动态</span>
              </div>
            </div>

            <div class="feed-composer">
              <div class="avatar-sm">{{ profileInitial }}</div>
              <div class="feed-composer-main">
                <el-input v-model="postForm.content" type="textarea" :rows="3" placeholder="分享今天的打卡进展，例如跑步、背单词、阅读笔记" />
                <div class="feed-composer-actions">
                  <el-tag v-if="selectedCircle" effect="plain">{{ selectedCircle.name }}</el-tag>
                  <el-tag v-else type="info" effect="plain">未选择圈子</el-tag>
                  <el-button type="primary" :icon="Edit" :disabled="!selectedCircle?.joined" @click="publishPost">发布动态</el-button>
                </div>
              </div>
            </div>

            <div class="feed-heading">
              <div>
                <h3>最新动态</h3>
                <p>{{ selectedCircle ? selectedCircle.name : '全部圈子' }}</p>
              </div>
              <el-button text :icon="Refresh" :disabled="!selectedCircleId" @click="loadCirclePosts(selectedCircleId)">刷新</el-button>
            </div>
            <div class="post-list">
              <article v-for="post in circlePosts" :key="post.id" class="post-item">
                <div class="post-meta">
                  <div class="avatar-sm">{{ userInitial(post.author) }}</div>
                  <strong>{{ post.author.username }} · {{ post.circleName }}</strong>
                  <small>{{ post.createTime }}</small>
                </div>
                <div class="post-tags">
                  <el-tag v-if="post.postType === 'CHECK_IN'" type="success" effect="plain">打卡分享</el-tag>
                  <el-tag effect="plain">{{ visibilityLabel(post.visibility) }}</el-tag>
                </div>
                <p>{{ post.content }}</p>
                <div v-if="post.checkIn" class="post-checkin-card">
                  <span>{{ post.checkIn.goalType || '目标' }}</span>
                  <strong>{{ post.checkIn.goalName || goalName(post.checkIn.goalId) }}</strong>
                  <small>{{ post.checkIn.checkDate }} · {{ post.checkIn.makeup ? '补卡' : '今日打卡' }}</small>
                  <p v-if="post.checkIn.remark">{{ post.checkIn.remark }}</p>
                </div>
                <div class="post-actions">
                  <el-button size="small" :type="post.liked ? 'primary' : 'default'" @click="togglePostLike(post)">
                    {{ post.liked ? '已赞' : '点赞' }} {{ post.likeCount }}
                  </el-button>
                  <el-button size="small" @click="toggleComments(post)">
                    评论 {{ post.commentCount }}
                  </el-button>
                  <el-button size="small" type="success" @click="encouragePost(post)">
                    鼓励
                  </el-button>
                </div>
                <div v-if="expandedPostId === post.id" class="comment-box">
                  <div class="inline-form">
                    <el-input v-model="commentDrafts[post.id]" placeholder="写一条评论" @keyup.enter="submitComment(post)" />
                    <el-button type="primary" @click="submitComment(post)">发送</el-button>
                  </div>
                  <div class="comment-list">
                    <article v-for="comment in commentsByPost[post.id] || []" :key="comment.id" class="comment-item">
                      <strong>{{ comment.author.username }}</strong>
                      <span>{{ comment.content }}</span>
                    </article>
                    <el-empty v-if="(commentsByPost[post.id] || []).length === 0" description="还没有评论" />
                  </div>
                </div>
              </article>
              <el-empty v-if="circlePosts.length === 0" description="选择一个圈子查看或发布动态" />
            </div>
          </section>

          <aside class="community-aside">
            <section class="panel community-summary">
              <div class="panel-head">
                <div>
                  <h3>我的圈子</h3>
                  <p class="panel-copy">{{ joinedCircles.length }} 个圈子正在关注</p>
                </div>
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="joined-circle-list">
                <button
                  v-for="circle in joinedCircles"
                  :key="circle.id"
                  class="joined-circle"
                  :class="{ active: selectedCircleId === circle.id }"
                  type="button"
                  @click="selectCircle(circle)"
                >
                  <span class="circle-icon">{{ circle.icon || 'TAG' }}</span>
                  <span>
                    <strong>{{ circle.name }}</strong>
                    <small>{{ circle.memberCount }} 人</small>
                  </span>
                </button>
                <el-empty v-if="joinedCircles.length === 0" description="尚未加入圈子" />
              </div>
            </section>

            <section class="panel community-summary">
              <div class="panel-head">
                <div>
                  <h3>社区动态</h3>
                  <p class="panel-copy">{{ feedPosts.length }} 条汇总动态</p>
                </div>
                <el-icon><Bell /></el-icon>
              </div>
              <article v-for="post in feedPosts.slice(0, 3)" :key="post.id" class="feed-mini-post" @click="socialTab = 'feed'">
                <strong>{{ post.author.username }} · {{ post.circleName }}</strong>
                <p>{{ post.content }}</p>
              </article>
              <el-empty v-if="feedPosts.length === 0" description="暂无动态" />
              <el-button class="full-button" @click="socialTab = 'feed'">查看全部动态</el-button>
            </section>
          </aside>
        </div>

        <section v-if="socialTab === 'feed'" class="panel feed-panel">
          <div class="feed-heading">
            <div>
              <h3>社区动态</h3>
              <p>你加入的圈子动态会汇总在这里。</p>
            </div>
            <el-button text :icon="Refresh" @click="loadSocialData">刷新</el-button>
          </div>
          <div class="post-list">
              <article v-for="post in feedPosts" :key="post.id" class="post-item">
                <div class="post-meta">
                  <div class="avatar-sm">{{ userInitial(post.author) }}</div>
                  <strong>{{ post.author.username }} · {{ post.circleName }}</strong>
                  <small>{{ post.createTime }}</small>
                </div>
                <div class="post-tags">
                  <el-tag v-if="post.postType === 'CHECK_IN'" type="success" effect="plain">打卡分享</el-tag>
                  <el-tag effect="plain">{{ visibilityLabel(post.visibility) }}</el-tag>
                </div>
                <p>{{ post.content }}</p>
                <div v-if="post.checkIn" class="post-checkin-card">
                  <span>{{ post.checkIn.goalType || '目标' }}</span>
                  <strong>{{ post.checkIn.goalName || goalName(post.checkIn.goalId) }}</strong>
                  <small>{{ post.checkIn.checkDate }} · {{ post.checkIn.makeup ? '补卡' : '今日打卡' }}</small>
                  <p v-if="post.checkIn.remark">{{ post.checkIn.remark }}</p>
                </div>
                <div class="post-actions">
                <el-button size="small" :type="post.liked ? 'primary' : 'default'" @click="togglePostLike(post)">
                  {{ post.liked ? '已赞' : '点赞' }} {{ post.likeCount }}
                </el-button>
                <el-button size="small" @click="toggleComments(post)">
                  评论 {{ post.commentCount }}
                </el-button>
                <el-button size="small" type="success" @click="encouragePost(post)">
                  鼓励
                </el-button>
              </div>
              <div v-if="expandedPostId === post.id" class="comment-box">
                <div class="inline-form">
                  <el-input v-model="commentDrafts[post.id]" placeholder="写一条评论" @keyup.enter="submitComment(post)" />
                  <el-button type="primary" @click="submitComment(post)">发送</el-button>
                </div>
                <div class="comment-list">
                  <article v-for="comment in commentsByPost[post.id] || []" :key="comment.id" class="comment-item">
                    <strong>{{ comment.author.username }}</strong>
                    <span>{{ comment.content }}</span>
                  </article>
                  <el-empty v-if="(commentsByPost[post.id] || []).length === 0" description="还没有评论" />
                </div>
              </div>
            </article>
            <el-empty v-if="feedPosts.length === 0" description="加入圈子后即可查看动态流" />
          </div>
        </section>

        <section v-if="socialTab === 'leaderboard'" class="leaderboard-workspace">
          <section class="panel leaderboard-panel">
            <div class="panel-head">
              <div>
                <h3>好友排行榜</h3>
                <p class="panel-copy">按累计打卡次数排序。</p>
              </div>
              <el-icon><Medal /></el-icon>
            </div>
            <div class="leaderboard-list">
              <article
                v-for="item in friendLeaderboard"
                :key="item.user.id"
                class="leaderboard-row"
                :class="{ podium: item.rank <= 3, mine: item.isMe }"
              >
                <span class="rank-number">{{ item.rank }}</span>
                <div class="avatar-sm">{{ userInitial(item.user) }}</div>
                <div class="leaderboard-main">
                  <strong>{{ item.user.username }}</strong>
                  <small>{{ item.isMe ? '我' : item.user.email || '好友' }}</small>
                </div>
                <div class="leaderboard-score">
                  <strong>{{ item.checkInCount }}</strong>
                  <span>次打卡</span>
                </div>
              </article>
              <el-empty v-if="friendLeaderboard.length === 0" description="添加好友后即可查看排行" />
            </div>
          </section>

          <section class="panel leaderboard-panel">
            <div class="panel-head">
              <div>
                <h3>圈子排行榜</h3>
                <p class="panel-copy">按圈子成员累计打卡次数排序。</p>
              </div>
              <el-icon><Medal /></el-icon>
            </div>
            <div class="leaderboard-list">
              <article
                v-for="item in circleLeaderboard"
                :key="item.circle.id"
                class="leaderboard-row circle"
                :class="{ podium: item.rank <= 3 }"
              >
                <span class="rank-number">{{ item.rank }}</span>
                <div class="circle-icon">{{ item.circle.icon || 'TAG' }}</div>
                <div class="leaderboard-main">
                  <strong>{{ item.circle.name }}</strong>
                  <small>{{ item.circle.memberCount }} 人 · {{ item.circle.joined ? '已加入' : '未加入' }}</small>
                </div>
                <div class="leaderboard-score">
                  <strong>{{ item.checkInCount }}</strong>
                  <span>次打卡</span>
                </div>
              </article>
              <el-empty v-if="circleLeaderboard.length === 0" description="暂无圈子排行" />
            </div>
          </section>
        </section>
        </section>
      </div>

      <div v-if="activeView === 'profile'" class="profile-layout profile-workspace">
        <section class="panel profile-card profile-summary-card">
          <div class="profile-cover">
            <div class="profile-particles" aria-hidden="true">
              <i
                v-for="particle in profileParticles"
                :key="particle.id"
                :style="{
                  left: particle.left,
                  top: particle.top,
                  width: particle.size,
                  height: particle.size,
                  animationDelay: particle.delay,
                  animationDuration: particle.duration
                }"
              ></i>
            </div>
            <div class="profile-avatar">{{ profileInitial }}</div>
            <div>
              <h3>{{ profile?.username }}</h3>
              <p>{{ profile?.email || '暂未填写邮箱' }}</p>
              <div class="profile-badges">
                <span>协作账号</span>
                <span>{{ dashboard?.currentStreakDays ?? 0 }} 天连续</span>
              </div>
            </div>
          </div>
          <div class="profile-stats">
            <span><strong>{{ dashboard?.totalGoals ?? 0 }}</strong>目标</span>
            <span><strong>{{ dashboard?.totalCheckIns ?? 0 }}</strong>打卡</span>
            <span><strong>{{ dashboard?.currentStreakDays ?? 0 }}</strong>连续天数</span>
          </div>
          <div class="profile-progress">
            <div>
              <span>自律完成率</span>
              <strong>{{ dashboard?.averageCompletionRate ?? 0 }}%</strong>
            </div>
            <el-progress :percentage="dashboard?.averageCompletionRate ?? 0" :show-text="false" />
          </div>
          <div class="profile-summary-list">
            <article>
              <span>账号状态</span>
              <strong>正常使用</strong>
              <small>资料、目标和打卡记录会自动同步。</small>
            </article>
            <article>
              <span>协作身份</span>
              <strong>{{ profile?.username || 'HabitFlow 用户' }}</strong>
              <small>可与好友互发提醒、评论圈子动态。</small>
            </article>
            <article>
              <span>账号加入</span>
              <strong>{{ profileActiveDays }} 天</strong>
              <small>已获 {{ badges.length }} 枚勋章。</small>
            </article>
          </div>
        </section>

        <section class="profile-settings-stack">
          <section class="panel profile-settings profile-primary">
            <div class="panel-head">
              <div>
                <h3>基础资料</h3>
                <p class="panel-copy">维护你在 HabitFlow 中展示的基本资料。</p>
              </div>
              <el-icon><User /></el-icon>
            </div>
            <el-form class="profile-form-grid" :model="profileForm" label-position="top">
              <el-form-item label="显示名称">
                <el-input v-model="profileForm.username" placeholder="输入新的展示名称" maxlength="50" show-word-limit />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="profileForm.email" />
              </el-form-item>
              <el-form-item label="当前用户名">
                <el-input :model-value="profile?.username || '-'" disabled />
              </el-form-item>
              <el-form-item label="账号创建时间">
                <el-input :model-value="formatDateTime(profile?.createTime)" disabled />
              </el-form-item>
              <div class="profile-form-actions">
                <el-button @click="resetProfileForm">恢复当前资料</el-button>
                <el-button type="primary" @click="saveProfile">保存改名</el-button>
              </div>
            </el-form>
          </section>

          <section class="panel account-status-card">
            <div class="panel-head">
              <div>
                <h3>账号概览</h3>
                <p class="panel-copy">查看你的协作、圈子和成长状态。</p>
              </div>
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="account-health-grid">
              <article>
                <span>同步状态</span>
                <strong>已同步</strong>
                <small>你的最新记录已保存。</small>
              </article>
              <article>
                <span>社交能力</span>
                <strong>{{ friends.length }} 位好友</strong>
                <small>可聊天、提醒和查看打卡状态。</small>
              </article>
              <article>
                <span>圈子参与</span>
                <strong>{{ joinedCircles.length }} 个圈子</strong>
                <small>发布运动、英语和阅读进度。</small>
              </article>
            </div>
          </section>

          <section class="panel security-card profile-security-card">
            <div class="panel-head">
              <div>
                <h3>安全与访问</h3>
                <p class="panel-copy">管理登录密码和当前登录状态。</p>
              </div>
              <el-icon><Lock /></el-icon>
            </div>
            <div class="security-action-list">
              <article class="security-row">
                <div>
                  <span>登录密码</span>
                  <strong>已加密保存</strong>
                  <small>进入弹窗后需要填写原密码和新密码。</small>
                </div>
                <el-button @click="openPasswordDialog">进入安全验证</el-button>
              </article>
              <article class="security-row">
                <div>
                  <span>当前会话</span>
                  <strong>已登录</strong>
                  <small>退出后需要重新输入账号和密码。</small>
                </div>
                <el-button :icon="SwitchButton" @click="logout">退出登录</el-button>
              </article>
            </div>
            <div class="security-timeline">
              <article>
                <span></span>
                <div>
                  <strong>密码保护</strong>
                  <small>密码不会在页面中明文展示。</small>
                </div>
              </article>
              <article>
                <span></span>
                <div>
                  <strong>账号范围</strong>
                  <small>你可以维护自己的资料、目标、好友关系和圈子内容。</small>
                </div>
              </article>
            </div>
          </section>
        </section>
      </div>
    </main>

    <el-dialog v-model="goalDialogVisible" :title="goalForm.id ? '编辑目标' : '新建目标'" width="520px">
      <el-form ref="goalFormRef" :model="goalForm" :rules="goalRules" label-position="top">
        <el-form-item label="目标名称" prop="name">
          <el-input v-model="goalForm.name" placeholder="每天运动30分钟" />
        </el-form-item>
        <el-form-item label="目标类型" prop="type">
          <el-select v-model="goalForm.type" class="full-button" filterable allow-create default-first-option placeholder="选择或输入类型">
            <el-option v-for="item in goalTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="重要程度">
          <el-segmented v-model="goalForm.priority" :options="priorityOptions" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="开始日期" prop="startDate">
            <el-date-picker v-model="goalForm.startDate" value-format="YYYY-MM-DD" type="date" class="full-button" />
          </el-form-item>
          <el-form-item label="结束日期" prop="endDate">
            <el-date-picker v-model="goalForm.endDate" value-format="YYYY-MM-DD" type="date" class="full-button" />
          </el-form-item>
        </div>
        <div class="form-grid">
          <el-form-item label="目标周期" prop="cycle">
            <el-select v-model="goalForm.cycle" class="full-button">
              <el-option label="每日" value="DAILY" />
              <el-option label="每周" value="WEEKLY" />
              <el-option label="每月" value="MONTHLY" />
            </el-select>
          </el-form-item>
          <el-form-item label="每日目标次数" prop="dailyTargetCount">
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

    <el-dialog v-model="calendarDialogVisible" :title="`${selectedCalendarDate} 日程安排`" width="560px" class="calendar-day-dialog">
      <div class="calendar-dialog-body">
        <p class="calendar-dialog-copy">
          日历格子里只保留一个紧急目标和一个其他目标，避免同一天任务过多时挤在一起。当天完整日程、优先级和打卡状态如下。
        </p>
        <div class="calendar-dialog-stats">
          <span>共 {{ selectedCalendarTasks.length }} 项</span>
          <span>已打卡 {{ selectedCalendarStats.done }} 项</span>
          <span>未打卡 {{ selectedCalendarStats.pending }} 项</span>
        </div>
        <article
          v-for="item in selectedCalendarTasks"
          :key="`dialog-${selectedCalendarDate}-${item.goal.id}`"
          class="calendar-dialog-task"
          :class="priorityClass(item.goal.priority)"
        >
          <div class="calendar-dialog-task-main">
            <strong>{{ item.goal.name }}</strong>
            <span>{{ item.goal.type }} · {{ cycleLabel(item.goal.cycle) }} · 每日 {{ item.goal.dailyTargetCount }} 次</span>
            <p v-if="item.checkIn?.remark">打卡备注：{{ item.checkIn.remark }}</p>
          </div>
          <div class="calendar-dialog-task-tags">
            <el-tag :type="priorityTagType(item.goal.priority)" effect="plain">{{ priorityLabel(item.goal.priority) }}</el-tag>
            <el-tag :type="taskCheckTagType(item)" effect="dark">{{ taskCheckStatusLabel(item) }}</el-tag>
          </div>
        </article>
        <el-empty v-if="selectedCalendarTasks.length === 0" description="当天暂无需要完成的任务" />
      </div>
      <template #footer>
        <el-button type="primary" @click="calendarDialogVisible = false">知道了</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="shareDialogVisible" title="分享本次打卡" width="560px" class="checkin-share-dialog">
      <div class="checkin-share-body">
        <p class="calendar-dialog-copy">
          打卡已完成，可以选择是否把本次完成情况同步到好友动态或圈子动态，让好友收到消息并一起监督。
          如果只想通知好友、不发布圈子动态，可以选择“仅自己可见”并保留好友通知。
        </p>
        <el-form :model="shareForm" label-position="top">
          <el-form-item label="分享内容">
            <el-input v-model="shareForm.content" type="textarea" :rows="4" maxlength="500" show-word-limit />
          </el-form-item>
          <el-form-item label="可见范围">
            <el-segmented v-model="shareForm.visibility" :options="visibilityOptions" />
          </el-form-item>
          <el-form-item v-if="shareForm.visibility !== 'PRIVATE'" label="发布到圈子">
            <el-select v-model="shareForm.circleId" class="full-button" placeholder="选择圈子">
              <el-option
                v-for="circle in circles.filter((item) => item.joined)"
                :key="circle.id"
                :label="circle.name"
                :value="circle.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="好友通知">
            <el-checkbox v-model="shareForm.shareToFriends">发送打卡完成消息给好友</el-checkbox>
          </el-form-item>
          <el-form-item v-if="shareForm.shareToFriends" label="通知好友">
            <el-select v-model="shareForm.friendIds" multiple collapse-tags collapse-tags-tooltip class="full-button" placeholder="默认选择全部好友">
              <el-option v-for="friend in friends" :key="friend.id" :label="friend.username" :value="friend.id" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="shareDialogVisible = false">不分享</el-button>
        <el-button type="primary" @click="submitShareCheckIn">确认分享</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="420px">
      <el-form :model="passwordForm" label-position="top">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword">更新密码</el-button>
      </template>
    </el-dialog>

    <transition name="inspiration-fade">
      <div v-if="inspirationVisible" class="inspiration-overlay" @click.self="closeInspiration">
        <section class="inspiration-card" role="dialog" aria-modal="true" aria-labelledby="inspiration-title">
          <div class="confetti-field" aria-hidden="true">
            <i
              v-for="piece in inspirationConfetti"
              :key="piece.id"
              :style="{
                '--x': piece.x,
                '--delay': piece.delay,
                '--duration': piece.duration,
                '--rotate': piece.rotate,
                '--rotate-end': piece.rotateEnd,
                background: piece.color
              }"
            ></i>
          </div>
          <button class="inspiration-close" type="button" aria-label="关闭" @click="closeInspiration">x</button>
          <div class="success-ring">
            <el-icon><Check /></el-icon>
          </div>
          <p class="inspiration-kicker">打卡完成</p>
          <h3 id="inspiration-title">今天也认真完成了一步</h3>
          <blockquote>{{ inspirationCard.content }}</blockquote>
          <p v-if="inspirationCard.cn" class="inspiration-cn">{{ inspirationCard.cn }}</p>
          <p v-if="inspirationCard.example" class="inspiration-example">例句：{{ inspirationCard.example }}</p>
          <div v-if="inspirationCard.peerTips.length > 0" class="peer-tip-list">
            <strong>同路人寄语</strong>
            <article v-for="tip in inspirationCard.peerTips" :key="`${tip.goalName}-${tip.remark}`">
              <span>「{{ tip.remark }}」</span>
              <small>{{ tip.goalName }}</small>
            </article>
          </div>
          <div class="inspiration-actions">
            <el-button class="inspiration-action" @click="closeInspiration">继续坚持</el-button>
            <el-button
              v-if="pendingShareData"
              type="primary"
              class="inspiration-action"
              @click="shareFromInspiration"
            >
              分享打卡
            </el-button>
          </div>
        </section>
      </div>
    </transition>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Aim, Bell, Calendar, Check, DataAnalysis, Download, Edit, Lock, Medal, Plus, Refresh, SwitchButton, Timer, User } from '@element-plus/icons-vue'
import { authApi, badgeApi, checkInApi, exportApi, goalApi, notificationApi, socialApi, statsApi, userApi } from './api'

const token = ref(localStorage.getItem('habitflow_token'))
const profile = ref(JSON.parse(localStorage.getItem('habitflow_profile') || 'null'))
const authMode = ref('login')
const authLoading = ref(false)
const activeView = ref('dashboard')
const mobileNavOpen = ref(false)
const authForm = reactive({ username: '', password: '', email: '' })
const authFormRef = ref()
const authParticleCanvasRef = ref()
const dashboard = ref(null)
const goalRows = ref([])
const checkIns = ref([])
const calendarCheckIns = ref([])
const badges = ref([])
const notifications = ref([])
const notificationUnreadCount = ref(0)
const socialUsers = ref([])
const friends = ref([])
const friendRequests = ref([])
const friendCheckinBoard = ref([])
const friendLeaderboard = ref([])
const circleLeaderboard = ref([])
const circles = ref([])
const circlePosts = ref([])
const feedPosts = ref([])
const monthlyChartRef = ref()
const rateChartRef = ref()
const calendarDate = ref(new Date())
const calendarDialogVisible = ref(false)
const selectedCalendarDate = ref('')
let monthlyChart
let rateChart
let idleTimer = null
let authParticleFrame = 0
let authParticleStop = null

const IDLE_TIMEOUT_MS = 60 * 60 * 1000
const IDLE_CHECK_MS = 60 * 1000
const LAST_ACTIVITY_KEY = 'habitflow_last_activity'
const ACTIVITY_EVENTS = ['pointerdown', 'keydown', 'wheel', 'touchstart']

const goalDialogVisible = ref(false)
const goalFormRef = ref()
const goalForm = reactive(emptyGoal())
const checkForm = reactive({ goalId: null, remark: '' })
const makeupForm = reactive({ goalId: null, checkDate: '', remark: '' })
const recordFilters = reactive({ goalId: null, dateRange: [] })
const notificationFilters = reactive({ unreadOnly: false })
const notificationMode = ref('all')
const timelineList = ref([])
const timelineDays = ref(30)
const profileForm = reactive({ username: '', email: '' })
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const passwordDialogVisible = ref(false)
const inspirationVisible = ref(false)
const inspirationCard = reactive({ content: '', cn: '', example: '', peerTips: [] })
const shareDialogVisible = ref(false)
const latestCheckInShare = ref(null)
const pendingShareData = ref(null)
const shareForm = reactive({
  content: '',
  visibility: 'FRIENDS',
  circleId: null,
  shareToFriends: true,
  friendIds: []
})
const inspirationConfetti = Array.from({ length: 18 }, (_, index) => ({
  id: index,
  x: `${8 + ((index * 17) % 84)}%`,
  delay: `${(index % 6) * 0.08}s`,
  duration: `${1.4 + (index % 5) * 0.12}s`,
  rotate: `${(index * 47) % 180}deg`,
  rotateEnd: `${220 + ((index * 53) % 220)}deg`,
  color: ['#2f80ed', '#13a46f', '#f59f00', '#e03131', '#8b5cf6'][index % 5]
}))
const profileParticles = Array.from({ length: 24 }, (_, index) => ({
  id: index,
  left: `${4 + ((index * 19) % 92)}%`,
  top: `${8 + ((index * 23) % 78)}%`,
  size: `${3 + (index % 4)}px`,
  delay: `${(index % 8) * 0.18}s`,
  duration: `${4.6 + (index % 6) * 0.32}s`
}))
const userKeyword = ref('')
const socialTab = ref('friends')
const socialTabs = [
  { name: 'friends', kicker: '默认', label: '好友管理', description: '今日打卡、好友申请与同学搜索' },
  { name: 'chat', kicker: '私信', label: '好友聊天', description: '选择好友进入会话' },
  { name: 'circles', kicker: '社区', label: '圈子广场', description: '加入圈子并发布动态' },
  { name: 'feed', kicker: '动态', label: '社区动态', description: '汇总已加入圈子的消息流' },
  { name: 'leaderboard', kicker: '排行', label: '打卡排行榜', description: '查看好友和圈子打卡次数' }
]
const notificationTabs = [
  { name: 'all', kicker: '全部', label: '全部提醒', description: '查看所有待处理和历史提醒' },
  { name: 'unread', kicker: '优先', label: '未读提醒', description: '优先处理还没有确认的提醒' },
  { name: 'DAILY_CHECK_IN', kicker: '日常', label: '打卡提醒', description: '和今日目标相关的打卡消息' },
  { name: 'GOAL_EXPIRE', kicker: '到期', label: '目标预警', description: '临近结束日期的目标提醒' },
  { name: 'STREAK_BREAK', kicker: '连续', label: '中断提醒', description: '连续打卡节奏被打断时提示' }
]
const badgeRoadmap = [
  { name: '晨间启动者', description: '连续保持早起或晨间学习节奏。', condition: '连续 3 天完成任一早间目标' },
  { name: '英语听力周', description: '把英语听力练习稳定放进日程。', condition: '7 天内完成 5 次英语目标' },
  { name: '运动稳定器', description: '保持运动训练，不让节奏断掉。', condition: '累计完成 10 次运动打卡' },
  { name: '同伴鼓励者', description: '和好友互相提醒并分享进度。', condition: '完成好友提醒或圈子分享' }
]
const selectedChatFriendId = ref(null)
const chatMessages = ref([])
const messageForm = reactive({ content: '' })
const selectedCircleId = ref(null)
const circleForm = reactive({ name: '', description: '', icon: '' })
const postForm = reactive({ content: '' })
const expandedPostId = ref(null)
const commentDrafts = reactive({})
const commentsByPost = reactive({})
const statusOptions = [
  { label: '进行中', value: 'ACTIVE' },
  { label: '已暂停', value: 'PAUSED' },
  { label: '已完成', value: 'DONE' }
]
const navGroups = [
  {
    title: '目标',
    items: [
      { title: '任务日历', view: 'calendar', description: '按日期查看目标、优先级和打卡状态' },
      { title: '目标管理', view: 'goals', description: '创建、编辑、归档你的习惯目标' },
      { title: '打卡记录', view: 'checkins', description: '提交今日打卡或补录历史记录' }
    ]
  },
  {
    title: '成长',
    items: [
      { title: '成长日志', view: 'timeline', description: '回看坚持轨迹、备注和奖励事件' },
      { title: '消息提醒', view: 'notifications', description: '查看到期、断签和每日提醒' },
      { title: '勋章奖励', view: 'badges', description: '查看已经解锁的自律成就' }
    ]
  },
  {
    title: '社交',
    items: [
      { title: '社交圈子', view: 'social', description: '好友聊天、圈子动态和同伴监督' }
    ]
  },
  {
    title: '账号',
    items: [
      { title: '个人信息', view: 'profile', description: '维护资料、查看账号安全状态' }
    ]
  }
]
const authRevealItems = [
  {
    text: '运动打卡',
    images: [
      {
        src: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=320&auto=format&fit=crop&q=70',
        alt: '力量训练器械'
      },
      {
        src: 'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=320&auto=format&fit=crop&q=70',
        alt: '户外跑步训练'
      }
    ]
  },
  {
    text: '英语学习',
    images: [
      {
        src: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=320&auto=format&fit=crop&q=70',
        alt: '阅读学习笔记'
      },
      {
        src: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=320&auto=format&fit=crop&q=70',
        alt: '在线学习课程'
      }
    ]
  },
  {
    text: '好友监督',
    images: [
      {
        src: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=320&auto=format&fit=crop&q=70',
        alt: '朋友一起协作'
      },
      {
        src: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=320&auto=format&fit=crop&q=70',
        alt: '团队交流'
      }
    ]
  }
]
const priorityOptions = [
  { label: '普通', value: 'NORMAL' },
  { label: '重要', value: 'IMPORTANT' },
  { label: '紧急', value: 'URGENT' }
]
const visibilityOptions = [
  { label: '公开', value: 'PUBLIC' },
  { label: '好友可见', value: 'FRIENDS' },
  { label: '圈子可见', value: 'CIRCLE' },
  { label: '仅自己可见', value: 'PRIVATE' }
]
const encourageMessage = '坚持得很稳，继续保持。'
const goalTypeOptions = ['学习', '运动', '阅读', '英语', '早睡', '健身']
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const calendarVisibleGoalLimit = 2
const authRules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
  email: authMode.value === 'register'
    ? [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { pattern: emailPattern, message: '请输入有效邮箱', trigger: 'blur' }
      ]
    : []
}))
const goalRules = {
  name: [{ required: true, message: '请输入目标名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择或输入目标类型', trigger: 'change' }],
  startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  endDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  cycle: [{ required: true, message: '请选择目标周期', trigger: 'change' }],
  dailyTargetCount: [{ required: true, type: 'number', min: 1, message: '每日目标次数至少为 1', trigger: 'change' }]
}

const metrics = computed(() => [
  { label: '目标总数', value: dashboard.value?.totalGoals ?? 0, hint: '所有已创建目标' },
  { label: '进行中目标', value: dashboard.value?.activeGoals ?? 0, hint: '当前需要推进' },
  { label: '总完成次数', value: dashboard.value?.totalCheckIns ?? 0, hint: '累计打卡记录' },
  { label: '连续打卡天数', value: dashboard.value?.currentStreakDays ?? 0, hint: '保持节奏中' },
  { label: '平均完成率', value: `${dashboard.value?.averageCompletionRate ?? 0}%`, hint: '目标整体表现' }
])
const activeGoalRows = computed(() => goalRows.value.filter((item) => item.goal.status === 'ACTIVE'))

const todayGoals = computed(() => goalsForDate(new Date().toISOString().slice(0, 10)))
const todayDoneCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return todayGoals.value.filter((item) => checkInForGoalDate(item.goal.id, today)).length
})
const todayProgress = computed(() => {
  if (todayGoals.value.length === 0) return 0
  return Math.round((todayDoneCount.value / todayGoals.value.length) * 100)
})
const todayProgressStyle = computed(() => `${todayProgress.value}%`)
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})
const todayFocusText = computed(() => {
  if (todayGoals.value.length === 0) return '今天还没有安排目标，可以先去目标管理创建一个运动或英语打卡计划。'
  if (todayDoneCount.value === todayGoals.value.length) return '今日目标已经完成，可以去社交圈分享一下进展，顺手鼓励好友。'
  const nextGoal = todayGoals.value.find((item) => !checkInForGoalDate(item.goal.id, new Date().toISOString().slice(0, 10)))
  return `下一步建议完成「${nextGoal?.goal.name || '今日目标'}」，完成后系统会同步更新连续打卡与勋章。`
})
const selectedCalendarTasks = computed(() => tasksForDate(selectedCalendarDate.value))
const selectedCalendarStats = computed(() => {
  const done = selectedCalendarTasks.value.filter((item) => item.checkIn).length
  return {
    done,
    pending: selectedCalendarTasks.value.length - done
  }
})
const selectedChatFriend = computed(() => friends.value.find((friend) => friend.id === selectedChatFriendId.value))
const selectedCircle = computed(() => circles.value.find((circle) => circle.id === selectedCircleId.value))
const joinedCircles = computed(() => circles.value.filter((circle) => circle.joined))
const profileInitial = computed(() => (profile.value?.username || 'H').slice(0, 1).toUpperCase())
const profileActiveDays = computed(() => {
  if (!profile.value?.createTime) return 0
  const createdAt = new Date(profile.value.createTime)
  if (Number.isNaN(createdAt.getTime())) return 0
  const diff = Date.now() - createdAt.getTime()
  return Math.max(1, Math.ceil(diff / 86400000))
})
const currentNotificationTab = computed(() => (
  notificationTabs.find((tab) => tab.name === notificationMode.value) || notificationTabs[0]
))
const filteredNotifications = computed(() => {
  if (notificationMode.value === 'all') return notifications.value
  if (notificationMode.value === 'unread') return notifications.value.filter((item) => !item.read)
  return notifications.value.filter((item) => item.type === notificationMode.value)
})
const notificationActionCards = computed(() => [
  {
    kicker: '今日',
    title: todayGoals.value.length > 0 ? `${todayDoneCount.value}/${todayGoals.value.length} 个目标已打卡` : '今天暂无目标',
    description: todayGoals.value.length > todayDoneCount.value ? '先完成剩余目标，再把提醒标记为已读。' : '今天节奏不错，可以查看成长日志或分享给好友。'
  },
  {
    kicker: '提醒',
    title: `${notificationUnreadCount.value} 条未读消息`,
    description: notificationUnreadCount.value > 0 ? '建议先处理未读提醒，避免错过到期目标。' : '提醒已经清空，当前页面保持关注即可。'
  },
  {
    kicker: '连续',
    title: `${dashboard.value?.currentStreakDays ?? 0} 天连续打卡`,
    description: '连续记录会影响勋章和排行榜，尽量每天完成至少一次。'
  }
])
const badgeProgress = computed(() => {
  const total = badges.value.length + badgeRoadmap.length
  if (total === 0) return 0
  return Math.round((badges.value.length / total) * 100)
})
const badgePlanCards = computed(() => [
  {
    kicker: '下一步',
    title: todayGoals.value.length > todayDoneCount.value ? '完成今日剩余目标' : '保持连续打卡',
    description: todayGoals.value.length > todayDoneCount.value ? '优先完成今天还未打卡的目标。' : '今天已完成，可以准备明天的训练或学习安排。'
  },
  {
    kicker: '成长',
    title: `${dashboard.value?.totalCheckIns ?? 0} 次累计打卡`,
    description: '累计次数越高，越容易解锁长期坚持类勋章。'
  },
  {
    kicker: '社交',
    title: `${friends.value.length} 位好友监督`,
    description: '与好友互相提醒，可以让打卡更容易持续。'
  }
])

onMounted(() => {
  startSessionWatch()
  if (token.value) {
    loadAll().catch(() => {})
  } else {
    nextTick(startAuthParticles)
  }
})

onUnmounted(() => {
  stopSessionWatch()
  stopAuthParticles()
})

watch(token, async (value) => {
  if (value) {
    stopAuthParticles()
    return
  }
  await nextTick()
  startAuthParticles()
})

watch(activeView, () => {
  if (activeView.value === 'dashboard') {
    nextTick(() => {
      resetCharts()
      renderCharts()
    })
  }
  if (activeView.value === 'social') {
    loadSocialData()
  }
  if (activeView.value === 'notifications') {
    enterNotifications()
  }
})

watch(socialTab, () => {
  if (socialTab.value === 'chat') {
    prepareChat()
  }
})

function startAuthParticles() {
  stopAuthParticles()
  const canvas = authParticleCanvasRef.value
  if (!canvas || token.value) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const mouse = { x: -9999, y: -9999, active: false }
  const particles = []
  const config = {
    maxParticles: 180,
    minParticles: 92,
    density: 10500,
    connectDistance: 138,
    repelRadius: 170,
    repelForce: 5.8
  }

  function resize() {
    const rect = canvas.getBoundingClientRect()
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    canvas.width = Math.max(1, Math.floor(rect.width * dpr))
    canvas.height = Math.max(1, Math.floor(rect.height * dpr))
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    const targetCount = Math.max(
      config.minParticles,
      Math.min(config.maxParticles, Math.floor((rect.width * rect.height) / config.density))
    )
    while (particles.length < targetCount) particles.push(createParticle(rect.width, rect.height))
    particles.length = targetCount
  }

  function createParticle(width, height) {
    const hueShift = Math.random()
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.42,
      vy: (Math.random() - 0.5) * 0.42,
      radius: 1.35 + Math.random() * 1.75,
      color: hueShift > 0.56 ? 'rgba(20, 184, 166, 0.9)' : 'rgba(59, 130, 246, 0.92)'
    }
  }

  function updatePointer(event) {
    const rect = canvas.getBoundingClientRect()
    mouse.x = event.clientX - rect.left
    mouse.y = event.clientY - rect.top
    mouse.active = true
  }

  function clearPointer() {
    mouse.active = false
    mouse.x = -9999
    mouse.y = -9999
  }

  function tick() {
    const width = canvas.clientWidth
    const height = canvas.clientHeight
    ctx.clearRect(0, 0, width, height)

    for (let i = 0; i < particles.length; i += 1) {
      const a = particles[i]
      for (let j = i + 1; j < particles.length; j += 1) {
        const b = particles[j]
        const dx = a.x - b.x
        const dy = a.y - b.y
        const distance = Math.hypot(dx, dy)
        if (distance < config.connectDistance) {
          const alpha = (1 - distance / config.connectDistance) * 0.34
          ctx.beginPath()
          ctx.moveTo(a.x, a.y)
          ctx.lineTo(b.x, b.y)
          ctx.strokeStyle = `rgba(64, 126, 214, ${alpha})`
          ctx.lineWidth = 1
          ctx.stroke()
        }
      }
    }

    particles.forEach((particle) => {
      if (mouse.active) {
        const dx = particle.x - mouse.x
        const dy = particle.y - mouse.y
        const distance = Math.hypot(dx, dy)
        if (distance > 0 && distance < config.repelRadius) {
          const power = (1 - distance / config.repelRadius) ** 2
          particle.vx += (dx / distance) * power * config.repelForce
          particle.vy += (dy / distance) * power * config.repelForce
        }
      }

      particle.vx *= 0.93
      particle.vy *= 0.93
      particle.vx += (Math.random() - 0.5) * 0.035
      particle.vy += (Math.random() - 0.5) * 0.035
      particle.x += particle.vx
      particle.y += particle.vy

      if (particle.x < -12) particle.x = width + 12
      if (particle.x > width + 12) particle.x = -12
      if (particle.y < -12) particle.y = height + 12
      if (particle.y > height + 12) particle.y = -12

      const glow = ctx.createRadialGradient(particle.x, particle.y, 0, particle.x, particle.y, particle.radius * 5)
      glow.addColorStop(0, particle.color)
      glow.addColorStop(1, 'rgba(59, 130, 246, 0)')
      ctx.fillStyle = glow
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius * 5, 0, Math.PI * 2)
      ctx.fill()

      ctx.fillStyle = particle.color
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
      ctx.fill()
    })

    authParticleFrame = requestAnimationFrame(tick)
  }

  resize()
  window.addEventListener('resize', resize)
  window.addEventListener('pointermove', updatePointer)
  window.addEventListener('pointerleave', clearPointer)
  authParticleFrame = requestAnimationFrame(tick)
  authParticleStop = () => {
    cancelAnimationFrame(authParticleFrame)
    window.removeEventListener('resize', resize)
    window.removeEventListener('pointermove', updatePointer)
    window.removeEventListener('pointerleave', clearPointer)
    authParticleFrame = 0
    authParticleStop = null
  }
}

function stopAuthParticles() {
  if (authParticleStop) authParticleStop()
}

async function submitAuth() {
  await authFormRef.value?.validate()
  authLoading.value = true
  try {
    const data = authMode.value === 'login'
      ? await authApi.login(authForm)
      : await authApi.register(authForm)
    token.value = data.token
    profile.value = data.profile
    localStorage.setItem('habitflow_token', data.token)
    localStorage.setItem('habitflow_profile', JSON.stringify(data.profile))
    markUserActivity()
    Object.assign(profileForm, { username: data.profile.username, email: data.profile.email })
    await loadAll()
    activeView.value = 'dashboard'
    ElMessage.success('登录成功')
  } finally {
    authLoading.value = false
  }
}

async function loadAll() {
  if (!token.value) return
  const [profileData, statsData, goalsData, badgeData, timelineData] = await Promise.all([
    userApi.profile(),
    statsApi.dashboard(),
    goalApi.list(),
    badgeApi.mine(),
    statsApi.timeline(timelineDays.value)
  ])
  profile.value = profileData
  localStorage.setItem('habitflow_profile', JSON.stringify(profileData))
  Object.assign(profileForm, { username: profileData.username, email: profileData.email })
  dashboard.value = statsData
  goalRows.value = goalsData
  badges.value = badgeData
  timelineList.value = timelineData
  await loadCalendarCheckIns()
  await loadCheckIns()
  await loadNotifications()
  await loadSocialData()
  await nextTick()
  renderCharts()
}

async function loadSocialData() {
  if (!token.value) return
  const [friendsData, requestsData, circlesData, feedData, friendCheckinsData] = await Promise.all([
    socialApi.friends(),
    socialApi.friendRequests(),
    socialApi.circles(),
    socialApi.feed(),
    socialApi.friendsTodayCheckins()
  ])
  friends.value = friendsData
  friendRequests.value = requestsData
  circles.value = circlesData
  feedPosts.value = normalizeList(feedData)
  friendCheckinBoard.value = normalizeList(friendCheckinsData)
  try {
    const leaderboardData = await socialApi.leaderboards()
    friendLeaderboard.value = normalizeList(leaderboardData?.friends)
    circleLeaderboard.value = normalizeList(leaderboardData?.circles)
  } catch {
    friendLeaderboard.value = []
    circleLeaderboard.value = []
  }
  if (!selectedChatFriendId.value && friends.value.length > 0) {
    selectedChatFriendId.value = friends.value[0].id
  }
  if (selectedChatFriendId.value && friends.value.some((friend) => friend.id === selectedChatFriendId.value)) {
    await loadMessages(selectedChatFriendId.value)
  } else {
    selectedChatFriendId.value = null
    chatMessages.value = []
  }
  if (!selectedCircleId.value && circles.value.length > 0) {
    selectedCircleId.value = circles.value[0].id
  }
  if (selectedCircleId.value) {
    await loadCirclePosts(selectedCircleId.value)
  }
}

function renderCharts() {
  if (!monthlyChartRef.value || !rateChartRef.value) return
  monthlyChart = echarts.getInstanceByDom(monthlyChartRef.value) || echarts.init(monthlyChartRef.value)
  rateChart = echarts.getInstanceByDom(rateChartRef.value) || echarts.init(rateChartRef.value)
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
  nextTick(() => goalFormRef.value?.clearValidate())
  goalDialogVisible.value = true
}

async function saveGoal() {
  await goalFormRef.value?.validate()
  if (goalForm.endDate < goalForm.startDate) {
    ElMessage.warning('结束日期不能早于开始日期')
    return
  }
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
  ElMessage.success('目标已归档，历史记录已保留')
  await loadAll()
}

function showInspiration(data) {
  if (data?.inspiration) {
    const ins = data.inspiration
    Object.assign(inspirationCard, {
      content: ins.content || '坚持本身就是最好的证明。',
      cn: ins.cn || '',
      example: ins.example || '',
      peerTips: data.peerTips || []
    })
    inspirationVisible.value = false
    nextTick(() => {
      inspirationVisible.value = true
    })
  } else {
    ElMessage.success('打卡成功')
  }
}

function closeInspiration() {
  inspirationVisible.value = false
  pendingShareData.value = null
}

async function shareFromInspiration() {
  inspirationVisible.value = false
  if (pendingShareData.value) {
    const data = pendingShareData.value
    pendingShareData.value = null
    await loadSocialData()
    prepareShareDialog(data)
  }
}

function requestShareAfterCheckIn(data) {
  if (!data?.checkIn) return
  if (data?.inspiration) {
    pendingShareData.value = data
  } else {
    prepareShareDialog(data)
  }
}

function prepareShareDialog(data) {
  const checkIn = data?.checkIn
  if (!checkIn) return
  const goal = goalRows.value.find((item) => item.goal.id === checkIn.goalId)?.goal
  const firstJoinedCircle = circles.value.find((circle) => circle.joined)
  latestCheckInShare.value = { checkIn, goal }
  Object.assign(shareForm, {
    content: defaultShareContent(checkIn, goal),
    visibility: firstJoinedCircle ? 'CIRCLE' : 'PRIVATE',
    circleId: selectedCircleId.value || firstJoinedCircle?.id || null,
    shareToFriends: friends.value.length > 0,
    friendIds: friends.value.map((friend) => friend.id)
  })
  shareDialogVisible.value = true
}

function defaultShareContent(checkIn, goal) {
  const goalNameText = goal?.name || checkIn.goalName || goalName(checkIn.goalId)
  const goalTypeText = goal?.type || checkIn.goalType || '目标'
  const remarkText = checkIn.remark ? `，备注：${checkIn.remark}` : ''
  return `我刚刚完成了「${goalNameText}」打卡（${goalTypeText}）${remarkText}。一起坚持，互相监督！`
}

async function submitShareCheckIn() {
  if (!latestCheckInShare.value?.checkIn?.id) return
  if (!shareForm.content.trim()) {
    ElMessage.warning('请填写分享内容')
    return
  }
  if (shareForm.visibility !== 'PRIVATE' && !shareForm.circleId) {
    ElMessage.warning('请选择要发布到的圈子')
    return
  }
  const result = await socialApi.shareCheckIn({
    checkInId: latestCheckInShare.value.checkIn.id,
    content: shareForm.content.trim(),
    visibility: shareForm.visibility,
    circleId: shareForm.visibility === 'PRIVATE' ? null : shareForm.circleId,
    shareToFriends: shareForm.shareToFriends,
    friendIds: shareForm.shareToFriends ? shareForm.friendIds : []
  })
  shareDialogVisible.value = false
  await loadSocialData()
  if (result?.post) {
    selectedCircleId.value = result.post.circleId
    await loadCirclePosts(result.post.circleId)
    activeView.value = 'social'
    socialTab.value = 'circles'
    ElMessage.success('已同步到圈子动态')
  } else if (result?.notifiedFriendCount > 0) {
    activeView.value = 'social'
    socialTab.value = 'chat'
    prepareChat()
    ElMessage.success(`已通知 ${result.notifiedFriendCount} 位好友`)
  } else {
    ElMessage.success('打卡分享已处理')
  }
}

async function quickCheckIn(goal) {
  if (goal.status !== 'ACTIVE') {
    ElMessage.warning('只有进行中的目标可以打卡')
    return
  }
  const data = await checkInApi.create({ goalId: goal.id, remark: '快速打卡' })
  requestShareAfterCheckIn(data)
  showInspiration(data)
  await loadAll()
}

async function submitCheckIn(isMakeup) {
  const form = isMakeup ? makeupForm : checkForm
  if (!form.goalId) {
    ElMessage.warning('请选择目标')
    return
  }
  if (isMakeup && !form.checkDate) {
    ElMessage.warning('请选择补卡日期')
    return
  }
  let data
  if (isMakeup) {
    data = await checkInApi.makeup(form)
  } else {
    data = await checkInApi.create(form)
  }
  if (!isMakeup) {
    requestShareAfterCheckIn(data)
  }
  showInspiration(data)
  Object.assign(form, isMakeup ? { goalId: null, checkDate: '', remark: '' } : { goalId: null, remark: '' })
  await loadAll()
}

async function saveProfile() {
  if (!profileForm.username.trim()) {
    ElMessage.warning('请输入用户名')
    return
  }
  if (profileForm.email && !emailPattern.test(profileForm.email)) {
    ElMessage.warning('请输入有效邮箱')
    return
  }
  const data = await userApi.updateProfile(profileForm)
  profile.value = data
  localStorage.setItem('habitflow_profile', JSON.stringify(data))
  ElMessage.success('资料已更新')
}

function resetProfileForm() {
  Object.assign(profileForm, {
    username: profile.value?.username || '',
    email: profile.value?.email || ''
  })
}

async function changePassword() {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写原密码和新密码')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  await userApi.changePassword(passwordForm)
  Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
  passwordDialogVisible.value = false
  ElMessage.success('密码已更新')
}

function openPasswordDialog() {
  Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
  passwordDialogVisible.value = true
}

async function searchUsers() {
  if (!userKeyword.value.trim()) {
    socialUsers.value = []
    return
  }
  socialUsers.value = await socialApi.searchUsers(userKeyword.value.trim())
}

async function requestFriend(user) {
  await socialApi.requestFriend({ targetUserId: user.id, message: '一起坚持打卡吧' })
  ElMessage.success('好友申请已发送')
  await searchUsers()
  await loadSocialData()
}

async function handleFriendRequest(id, accepted) {
  if (accepted) {
    await socialApi.acceptFriend(id)
    ElMessage.success('已同意好友申请')
  } else {
    await socialApi.rejectFriend(id)
    ElMessage.success('已拒绝好友申请')
  }
  await loadSocialData()
}

async function prepareChat() {
  if (friends.value.length === 0) {
    await loadSocialData()
  }
  if (!selectedChatFriendId.value && friends.value.length > 0) {
    selectedChatFriendId.value = friends.value[0].id
  }
  if (selectedChatFriendId.value) {
    await loadMessages(selectedChatFriendId.value)
  }
}

async function openChat(friend) {
  selectedChatFriendId.value = friend.id
  socialTab.value = 'chat'
  await loadMessages(friend.id)
}

async function loadMessages(friendId) {
  if (!friendId) return
  chatMessages.value = await socialApi.messages(friendId)
}

async function sendMessage() {
  const content = messageForm.content.trim()
  if (!selectedChatFriendId.value || !content) return
  await socialApi.sendMessage(selectedChatFriendId.value, { content })
  messageForm.content = ''
  await loadMessages(selectedChatFriendId.value)
}

async function sendCheckinNudge(item) {
  const content = item.checkedIn
    ? `看到你今天完成了${item.doneCount}次打卡，很稳，明天继续一起坚持！`
    : '今天还没有看到你的打卡记录，记得完成目标呀，我们互相监督。'
  await socialApi.sendMessage(item.friend.id, { content })
  ElMessage.success(item.checkedIn ? '鼓励已发送' : '提醒已发送')
  if (selectedChatFriendId.value === item.friend.id) {
    await loadMessages(item.friend.id)
  }
}

async function createCircle() {
  await socialApi.createCircle({ ...circleForm })
  Object.assign(circleForm, { name: '', description: '', icon: '' })
  ElMessage.success('圈子已创建')
  await loadSocialData()
}

async function toggleCircle(circle) {
  if (circle.joined) {
    await socialApi.leaveCircle(circle.id)
    ElMessage.success('已退出圈子')
  } else {
    await socialApi.joinCircle(circle.id)
    ElMessage.success('已加入圈子')
  }
  await loadSocialData()
}

async function selectCircle(circle) {
  selectedCircleId.value = circle.id
  await loadCirclePosts(circle.id)
}

async function loadCirclePosts(circleId) {
  circlePosts.value = normalizeList(await socialApi.posts(circleId))
}

async function publishPost() {
  if (!selectedCircleId.value) return
  await socialApi.publishPost(selectedCircleId.value, { ...postForm })
  Object.assign(postForm, { content: '' })
  ElMessage.success('动态已发布')
  await loadCirclePosts(selectedCircleId.value)
  feedPosts.value = normalizeList(await socialApi.feed())
}

async function togglePostLike(post) {
  const data = post.liked
    ? await socialApi.unlikePost(post.id)
    : await socialApi.likePost(post.id)
  updatePostInteraction(post.id, { liked: data.liked, likeCount: data.likeCount })
}

async function toggleComments(post) {
  expandedPostId.value = expandedPostId.value === post.id ? null : post.id
  if (expandedPostId.value === post.id) {
    await loadComments(post.id)
  }
}

async function loadComments(postId) {
  commentsByPost[postId] = await socialApi.comments(postId)
}

async function submitComment(post) {
  const content = (commentDrafts[post.id] || '').trim()
  if (!content) return
  await socialApi.commentPost(post.id, { content })
  commentDrafts[post.id] = ''
  await loadComments(post.id)
  updatePostInteraction(post.id, { commentCount: (post.commentCount || 0) + 1 })
}

async function encouragePost(post) {
  await socialApi.commentPost(post.id, { content: encourageMessage })
  ElMessage.success('鼓励已发送')
  await loadComments(post.id)
  expandedPostId.value = post.id
  updatePostInteraction(post.id, { commentCount: (post.commentCount || 0) + 1 })
}

function updatePostInteraction(postId, patch) {
  for (const collection of [circlePosts.value, feedPosts.value]) {
    const target = collection.find((item) => item.id === postId)
    if (target) {
      Object.assign(target, patch)
    }
  }
}

function updateNavSpot(event) {
  const target = event.currentTarget
  const rect = target.getBoundingClientRect()
  target.style.setProperty('--spot-x', `${event.clientX - rect.left}px`)
  target.style.setProperty('--spot-y', `${event.clientY - rect.top}px`)
  target.style.setProperty('--spot-radius', `${Math.max(rect.width * 0.66, rect.height * 1.05, 52)}px`)
}

function startSessionWatch() {
  window.addEventListener('habitflow:auth-expired', handleAuthExpired)
  ACTIVITY_EVENTS.forEach((eventName) => {
    window.addEventListener(eventName, markUserActivity, { passive: true })
  })
  if (token.value && !localStorage.getItem(LAST_ACTIVITY_KEY)) {
    markUserActivity()
  }
  idleTimer = window.setInterval(checkIdleSession, IDLE_CHECK_MS)
  checkIdleSession()
}

function stopSessionWatch() {
  window.removeEventListener('habitflow:auth-expired', handleAuthExpired)
  ACTIVITY_EVENTS.forEach((eventName) => {
    window.removeEventListener(eventName, markUserActivity)
  })
  if (idleTimer) {
    window.clearInterval(idleTimer)
    idleTimer = null
  }
}

function markUserActivity() {
  if (!token.value) return
  localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()))
}

function checkIdleSession() {
  if (!token.value) return
  const lastActivity = Number(localStorage.getItem(LAST_ACTIVITY_KEY) || Date.now())
  if (Date.now() - lastActivity >= IDLE_TIMEOUT_MS) {
    clearSession()
    ElMessage.warning('已超过 1 小时未操作，请重新登录')
  }
}

function handleAuthExpired(event) {
  if (!token.value) return
  clearSession()
  ElMessage.warning(event.detail?.message || '登录状态已过期，请重新登录')
}

function selectView(view) {
  activeView.value = view
  if (view === 'social') {
    socialTab.value = 'friends'
  }
  mobileNavOpen.value = false
}

function openSocialSection(section) {
  socialTab.value = section
  if (section === 'chat') {
    prepareChat()
  }
}

function logout() {
  clearSession()
}

function clearSession() {
  localStorage.removeItem('habitflow_token')
  localStorage.removeItem('habitflow_profile')
  localStorage.removeItem(LAST_ACTIVITY_KEY)
  token.value = ''
  profile.value = null
  activeView.value = 'dashboard'
  mobileNavOpen.value = false
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
    const [startDate, endDate] = recordFilters.dateRange || []
    const blob = await exportApi.checkins({
      format: 'xlsx',
      goalId: recordFilters.goalId || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined
    })
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

async function loadCheckIns() {
  const [startDate, endDate] = recordFilters.dateRange || []
  checkIns.value = await checkInApi.list({
    goalId: recordFilters.goalId || undefined,
    start_date: startDate || undefined,
    end_date: endDate || undefined
  })
  monthlyChart.resize()
  rateChart.resize()
}

function resetCharts() {
  if (monthlyChart && monthlyChartRef.value !== monthlyChart.getDom()) {
    monthlyChart.dispose()
    monthlyChart = null
  }
  if (rateChart && rateChartRef.value !== rateChart.getDom()) {
    rateChart.dispose()
    rateChart = null
  }
}

async function loadNotifications() {
  const data = await notificationApi.list({
    unreadOnly: notificationFilters.unreadOnly,
    page: 1,
    pageSize: 50
  })
  notifications.value = normalizeList(data)
  notificationUnreadCount.value = data?.unreadCount || 0
}

async function enterNotifications() {
  notificationFilters.unreadOnly = false
  notificationMode.value = 'all'
  await loadNotifications()
  if (notificationUnreadCount.value > 0) {
    await notificationApi.markAllRead()
    notifications.value = notifications.value.map((item) => ({ ...item, read: true }))
    notificationUnreadCount.value = 0
  }
}

async function markNotificationRead(item) {
  await notificationApi.markRead(item.id)
  await loadNotifications()
}

async function markAllNotificationsRead() {
  await notificationApi.markAllRead()
  await loadNotifications()
  ElMessage.success('已全部标记为已读')
}

async function removeNotification(item) {
  await notificationApi.remove(item.id)
  await loadNotifications()
}

async function loadCalendarCheckIns() {
  calendarCheckIns.value = await checkInApi.list({})
}

function goalName(id) {
  return goalRows.value.find((item) => item.goal.id === id)?.goal.name || `目标 ${id}`
}

function formatDateTime(value) {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 16)
}

function cycleLabel(cycle) {
  return { DAILY: '每日', WEEKLY: '每周', MONTHLY: '每月' }[cycle] || cycle
}

function statusLabel(status) {
  return { ACTIVE: '进行中', PAUSED: '已暂停', DONE: '已完成' }[status] || status
}

function friendshipLabel(status) {
  return { NONE: '未添加', PENDING: '待处理', ACCEPTED: '已通过', REJECTED: '已拒绝' }[status] || status
}

function visibilityLabel(visibility) {
  return {
    PUBLIC: '公开',
    FRIENDS: '好友可见',
    CIRCLE: '圈子可见',
    PRIVATE: '仅自己可见'
  }[visibility] || '公开'
}

function formatTime(value) {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 16)
}

function userInitial(user) {
  return (user?.username || 'H').slice(0, 1).toUpperCase()
}

function priorityLabel(priority) {
  return { NORMAL: '普通', IMPORTANT: '重要', URGENT: '紧急' }[priority || 'NORMAL'] || '普通'
}

function priorityClass(priority) {
  return {
    NORMAL: 'priority-normal',
    IMPORTANT: 'priority-important',
    URGENT: 'priority-urgent'
  }[priority || 'NORMAL']
}

function priorityTagType(priority) {
  return { NORMAL: 'info', IMPORTANT: 'warning', URGENT: 'danger' }[priority || 'NORMAL'] || 'info'
}

function notificationTypeLabel(type) {
  return {
    DAILY_CHECK_IN: '日常打卡',
    GOAL_EXPIRE: '到期预警',
    STREAK_BREAK: '中断提醒'
  }[type] || '提醒'
}

function notificationTagType(type) {
  return {
    DAILY_CHECK_IN: 'primary',
    GOAL_EXPIRE: 'warning',
    STREAK_BREAK: 'danger'
  }[type] || 'info'
}

function notificationTypeClass(type) {
  return {
    DAILY_CHECK_IN: 'daily',
    GOAL_EXPIRE: 'expire',
    STREAK_BREAK: 'break'
  }[type] || 'normal'
}

function notificationCountByType(type) {
  return notifications.value.filter((item) => item.type === type).length
}

function dayNumber(day) {
  return Number(day.slice(-2))
}

function calendarSummaryForDate(day) {
  const tasks = tasksForDate(day)
  const urgentTasks = tasks.filter((item) => item.goal.priority === 'URGENT')
  const otherTasks = tasks.filter((item) => item.goal.priority !== 'URGENT')
  return [
    summaryItem('urgent', '紧急', 'URGENT', urgentTasks),
    summaryItem('other', '其他', otherTasks[0]?.goal.priority || 'NORMAL', otherTasks)
  ].filter(Boolean)
}

function calendarOverflowCount(day) {
  const total = goalsForDate(day).length
  return total > calendarVisibleGoalLimit ? total : 0
}

function summaryItem(key, label, priority, tasks) {
  if (tasks.length === 0) return null
  return {
    key,
    label,
    priority,
    title: tasks[0].goal.name,
    count: tasks.length
  }
}

function goalsForDate(day) {
  return goalRows.value
    .filter((item) => item.goal.status === 'ACTIVE')
    .filter((item) => item.goal.startDate <= day && item.goal.endDate >= day)
    .filter((item) => goalOccursOnDate(item.goal, day))
    .sort((left, right) => priorityRank(right.goal.priority) - priorityRank(left.goal.priority))
}

function tasksForDate(day) {
  if (!day) return []
  return goalsForDate(day).map((item) => ({
    ...item,
    checkIn: checkInForGoalDate(item.goal.id, day)
  }))
}

function checkInForGoalDate(goalId, day) {
  return calendarCheckIns.value.find((item) => item.goalId === goalId && item.checkDate === day)
}

function taskCheckStatusLabel(item) {
  if (!item.checkIn) return '未打卡'
  return item.checkIn.makeup ? '已补卡' : '已打卡'
}

function taskCheckTagType(item) {
  if (!item.checkIn) return 'info'
  return item.checkIn.makeup ? 'warning' : 'success'
}

function openCalendarDay(day) {
  selectedCalendarDate.value = day
  calendarDialogVisible.value = true
}

function goalOccursOnDate(goal, day) {
  const current = parseDate(day)
  const start = parseDate(goal.startDate)
  if (!current || !start) return false
  const dayDiff = Math.floor((current - start) / 86400000)
  if (goal.cycle === 'WEEKLY') return dayDiff % 7 === 0
  if (goal.cycle === 'MONTHLY') return current.getDate() === start.getDate()
  return true
}

function parseDate(value) {
  const date = new Date(`${value}T00:00:00`)
  return Number.isNaN(date.getTime()) ? null : date
}

function priorityRank(priority) {
  return { NORMAL: 1, IMPORTANT: 2, URGENT: 3 }[priority || 'NORMAL'] || 1
}

function normalizeList(data) {
  return Array.isArray(data) ? data : (data?.list || [])
}

function emptyGoal() {
  const today = new Date()
  const todayText = today.toISOString().slice(0, 10)
  return {
    id: null,
    name: '',
    type: '',
    startDate: todayText,
    endDate: todayText,
    cycle: 'DAILY',
    dailyTargetCount: 1,
    priority: 'NORMAL',
    status: 'ACTIVE'
  }
}
</script>
