<template>
  <div class="trip-list-page">
    <!-- 顶部操作栏 -->
    <header class="trip-list-page__header">
      <div class="trip-list-page__header-left">
        <h1>我的行程</h1>
        <span class="trip-list-page__username">{{ userStore.username }}</span>
      </div>
      <div class="trip-list-page__header-right">
        <el-button type="primary" @click="showPlanDialog = true">
          <el-icon><MagicStick /></el-icon> AI 帮我规划
        </el-button>
        <el-button @click="showFormDialog = true">
          <el-icon><Plus /></el-icon> 新建行程
        </el-button>
        <el-button text @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <!-- 筛选栏 -->
    <div class="trip-list-page__filters">
      <el-input
        v-model="filterCity"
        placeholder="按城市筛选"
        clearable
        style="width: 200px"
      />
      <el-date-picker
        v-model="filterDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        style="width: 280px"
      />
      <span class="trip-list-page__total-budget" v-if="totalBudget > 0">
        总预算：<strong>¥{{ totalBudget }}</strong>
      </span>
    </div>

    <!-- TODO: P4 实现 — 行程卡片按日期分组展示 -->
    <!-- 空状态 -->
    <div class="trip-list-page__empty" v-if="true">
      <el-empty description="还没有行程">
        <el-button type="primary" @click="showPlanDialog = true">
          让 AI 帮你规划
        </el-button>
      </el-empty>
    </div>

    <!-- 行程编辑弹窗 -->
    <TripFormDialog
      v-model:visible="showFormDialog"
      @saved="handleSaved"
    />

    <!-- AI 规划弹窗 -->
    <AIPlanDialog
      v-model:visible="showPlanDialog"
      @saved="handleSaved"
    />

    <!-- AI 文案弹窗 -->
    <!-- TODO: P4 实现 — 从 TripCard 的 @copywriting 事件触发此弹窗 -->
    <AICopywritingDialog
      v-model:visible="showCopywritingDialog"
      :trip="selectedTrip"
    />
  </div>
</template>

<script setup>
// TODO: P4 实现 — 列表数据加载、筛选联动、预算统计
import { ref } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import TripFormDialog from '../components/TripFormDialog.vue'
import AIPlanDialog from '../components/AIPlanDialog.vue'
import AICopywritingDialog from '../components/AICopywritingDialog.vue'

const userStore = useUserStore()
const router = useRouter()

const filterCity = ref('')
const filterDateRange = ref([])
const totalBudget = ref(0)
const showFormDialog = ref(false)
const showPlanDialog = ref(false)
const showCopywritingDialog = ref(false)
const selectedTrip = ref(null)

const handleLogout = () => {
  userStore.clearAuth()
  router.push('/login')
}

const handleSaved = () => {
  // TODO: P4 实现 — 刷新列表
}
</script>

<style scoped>
.trip-list-page {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}
.trip-list-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}
.trip-list-page__header-left {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-md);
}
.trip-list-page__header-left h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}
.trip-list-page__username {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
.trip-list-page__header-right {
  display: flex;
  gap: var(--spacing-sm);
}
.trip-list-page__filters {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}
.trip-list-page__total-budget {
  margin-left: auto;
  font-size: var(--font-size-md);
  color: var(--text-secondary);
}
.trip-list-page__total-budget strong {
  color: var(--color-accent);
}
.trip-list-page__empty {
  padding: var(--spacing-xl) 0;
}
</style>
