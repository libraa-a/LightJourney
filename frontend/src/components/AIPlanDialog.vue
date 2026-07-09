<template>
  <el-dialog
    :model-value="visible"
    title="AI 智能规划行程"
    width="780px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @open="handleDialogOpen"
  >
    <!-- 步骤条 -->
    <el-steps :active="step" finish-status="success" align-center class="plan-steps">
      <el-step title="填写参数" />
      <el-step title="预览编辑" />
      <el-step title="确认保存" />
    </el-steps>

    <!-- ==================== Step 0: 参数填写 ==================== -->
    <div v-if="step === 0" class="plan-step-content">
      <el-form ref="paramFormRef" :model="params" :rules="paramRules" label-width="80px" size="default">
        <el-form-item label="目的地" prop="city">
          <el-input v-model="params.city" placeholder="如：成都" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="params.start_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="params.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="偏好" prop="preferences">
          <el-checkbox-group v-model="params.preferences">
            <el-checkbox label="美食">美食</el-checkbox>
            <el-checkbox label="自然风光">自然风光</el-checkbox>
            <el-checkbox label="人文历史">人文历史</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="预算上限">
          <el-input-number v-model="params.budget" :min="0" :step="100" placeholder="选填，不限" style="width: 100%" />
        </el-form-item>
      </el-form>
      <div class="plan-step-actions">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="generating" @click="handleGenerate">
          生成行程
        </el-button>
      </div>
    </div>

    <!-- ==================== Step 1: 预览编辑 ==================== -->
    <div v-else-if="step === 1" class="plan-step-content">
      <div v-if="planItems.length === 0" class="plan-empty">
        <el-empty description="暂无生成的行程" />
      </div>

      <div v-else class="plan-preview">
        <!-- 按日期分组 -->
        <div v-for="(group, date) in groupedPlan" :key="date" class="plan-group">
          <div class="plan-group__header">
            <span class="plan-group__date">{{ date }}</span>
            <span class="plan-group__count">{{ group.length }} 条行程</span>
          </div>

          <!-- 行程卡片 -->
          <div
            v-for="(item, idx) in group"
            :key="item._key"
            class="plan-item"
            :class="{
              'plan-item--internal-conflict': item._conflictType === 'internal',
              'plan-item--external-conflict': item._conflictType === 'external',
              'plan-item--deleted': item._deleted,
            }"
          >
            <!-- 摘要行 -->
            <div class="plan-item__summary" @click="toggleEdit(item)">
              <div class="plan-item__time">
                <el-icon :size="14"><Clock /></el-icon>
                {{ item.start_time }} - {{ item.end_time }}
              </div>
              <div class="plan-item__title">{{ item.title }}</div>
              <div class="plan-item__budget" v-if="item.budget > 0">¥{{ item.budget }}</div>
              <div class="plan-item__conflict-tag">
                <el-tag v-if="item._conflictType === 'internal'" type="warning" size="small" effect="plain">
                  内部时段重叠
                </el-tag>
                <el-tag v-if="item._conflictType === 'external'" type="danger" size="small" effect="plain">
                  {{ item._conflictInfo }}
                </el-tag>
              </div>
              <el-button
                text
                type="danger"
                size="small"
                @click.stop="removeItem(item)"
                :disabled="item._deleted"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>

            <!-- 展开编辑面板 -->
            <div v-if="item._editing && !item._deleted" class="plan-item__edit">
              <el-row :gutter="12">
                <el-col :span="8">
                  <label class="plan-item__label">日期</label>
                  <el-date-picker
                    v-model="item.date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    size="small"
                    style="width: 100%"
                  />
                </el-col>
                <el-col :span="8">
                  <label class="plan-item__label">开始时间</label>
                  <el-time-picker
                    v-model="item.start_time"
                    format="HH:mm"
                    value-format="HH:mm"
                    size="small"
                    style="width: 100%"
                  />
                </el-col>
                <el-col :span="8">
                  <label class="plan-item__label">结束时间</label>
                  <el-time-picker
                    v-model="item.end_time"
                    format="HH:mm"
                    value-format="HH:mm"
                    size="small"
                    style="width: 100%"
                  />
                </el-col>
              </el-row>
              <el-row :gutter="12" style="margin-top: 8px">
                <el-col :span="16">
                  <label class="plan-item__label">标题</label>
                  <el-input v-model="item.title" size="small" />
                </el-col>
                <el-col :span="8">
                  <label class="plan-item__label">预算（元）</label>
                  <el-input-number
                    v-model="item.budget"
                    :min="0"
                    :precision="2"
                    :step="10"
                    size="small"
                    style="width: 100%"
                  />
                </el-col>
              </el-row>
              <div style="margin-top: 8px" v-if="item.description !== undefined">
                <label class="plan-item__label">描述</label>
                <el-input v-model="item.description" type="textarea" :rows="2" size="small" />
              </div>
              <div class="plan-item__edit-actions">
                <el-button size="small" @click="item._editing = false">收起</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 图例 -->
        <div class="plan-legend" v-if="hasConflicts">
          <span class="plan-legend__item plan-legend__internal">■ 内部冲突（不阻断保存）</span>
          <span class="plan-legend__item plan-legend__external">■ 与已有行程冲突（保存时跳过）</span>
        </div>
      </div>

      <div class="plan-step-actions">
        <el-button @click="step = 0">返回修改参数</el-button>
        <el-button type="primary" @click="goToConfirm">
          下一步：确认保存（{{ activeCount }} 条）
        </el-button>
      </div>
    </div>

    <!-- ==================== Step 2: 确认保存 ==================== -->
    <div v-else class="plan-step-content">
      <div class="plan-confirm">
        <div class="plan-confirm__summary">
          <p>共 <strong>{{ activeCount }}</strong> 条行程待保存</p>
          <p v-if="externalConflictCount > 0" class="plan-confirm__warn">
            ⚠ 其中 <strong>{{ externalConflictCount }}</strong> 条与已有行程冲突，将被跳过
          </p>
          <p v-if="deletedCount > 0" class="plan-confirm__note">
            {{ deletedCount }} 条已被删除，不会保存
          </p>
        </div>

        <!-- 简要列表 -->
        <div class="plan-confirm__list">
          <div
            v-for="item in confirmList"
            :key="item._key"
            class="plan-confirm__item"
            :class="{ 'plan-confirm__item--skip': item._conflictType === 'external' }"
          >
            <el-icon v-if="item._conflictType !== 'external'" class="plan-confirm__check" color="#7D9B76">
              <Check />
            </el-icon>
            <el-icon v-else class="plan-confirm__check" color="#E57373">
              <Close />
            </el-icon>
            <span class="plan-confirm__item-date">{{ item.date }}</span>
            <span class="plan-confirm__item-title">{{ item.title }}</span>
            <span v-if="item._conflictType === 'external'" class="plan-confirm__item-reason">
              {{ item._conflictInfo }}
            </span>
          </div>
        </div>

        <!-- 保存结果 -->
        <div v-if="saveResult" class="plan-confirm__result">
          <el-alert
            :type="saveResult.failed === 0 ? 'success' : 'warning'"
            :closable="false"
            show-icon
          >
            <template #title>
              已保存 {{ saveResult.saved }} 条行程
              <template v-if="saveResult.failed > 0">
                ，{{ saveResult.failed }} 条因时段冲突未保存
              </template>
            </template>
          </el-alert>
        </div>
      </div>

      <div class="plan-step-actions">
        <el-button @click="step = 1" :disabled="saving">返回编辑</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave" :disabled="saveResult !== null">
          {{ saveResult ? '保存完成' : '确认保存' }}
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Delete, Check, Close } from '@element-plus/icons-vue'
import { planTrip } from '../api/ai'
import { createTrip } from '../api/trips'

defineProps({
  visible: { type: Boolean, default: false },
})
const emit = defineEmits(['update:visible', 'saved'])

// ----- 状态 -----
const step = ref(0)
const generating = ref(false)
const saving = ref(false)
const planItems = ref([])
const saveResult = ref(null)
const paramFormRef = ref(null)

const params = reactive({
  city: '',
  start_date: '',
  end_date: '',
  preferences: [],
  budget: null,
})

// 日期校验
const validateDateRange = (_rule, _value, callback) => {
  if (params.start_date && params.end_date && params.end_date < params.start_date) {
    callback(new Error('结束日期不能早于开始日期'))
  } else {
    callback()
  }
}

const paramRules = {
  city: [{ required: true, message: '请输入目的地', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    { validator: validateDateRange, trigger: 'change' },
  ],
  preferences: [
    { type: 'array', min: 1, message: '请至少选择一个偏好', trigger: 'change' },
  ],
}

// ----- 计算属性 -----
const groupedPlan = computed(() => {
  const groups = {}
  planItems.value
    .filter((item) => !item._deleted)
    .forEach((item) => {
      if (!groups[item.date]) groups[item.date] = []
      groups[item.date].push(item)
    })
  // 按日期排序
  const sorted = {}
  Object.keys(groups)
    .sort()
    .forEach((k) => (sorted[k] = groups[k]))
  return sorted
})

const activeCount = computed(() => planItems.value.filter((i) => !i._deleted).length)
const deletedCount = computed(() => planItems.value.filter((i) => i._deleted).length)
const externalConflictCount = computed(
  () => planItems.value.filter((i) => !i._deleted && i._conflictType === 'external').length
)
const hasConflicts = computed(() =>
  planItems.value.some((i) => i._conflictType)
)

const confirmList = computed(() =>
  planItems.value.filter((i) => !i._deleted)
)

// ----- 方法 -----

/** 弹窗打开时重置状态 */
function handleDialogOpen() {
  step.value = 0
  planItems.value = []
  saveResult.value = null
}

/** 判断两个时段是否重叠（等于不重叠） */
function timeOverlap(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && aEnd > bStart
}

/** 检测 AI 生成行程之间的内部冲突 */
function detectInternalConflicts(items) {
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      if (items[i].date !== items[j].date) continue
      if (timeOverlap(items[i].start_time, items[i].end_time, items[j].start_time, items[j].end_time)) {
        items[i]._conflictType = 'internal'
        items[i]._conflictInfo = `与"${items[j].title}"时段重叠`
        items[j]._conflictType = 'internal'
        items[j]._conflictInfo = `与"${items[i].title}"时段重叠`
      }
    }
  }
}

/** 标记外部冲突 */
function markExternalConflicts(items, conflicts) {
  if (!conflicts || conflicts.length === 0) return
  conflicts.forEach((c) => {
    const idx = c.plan_index
    if (idx >= 0 && idx < items.length) {
      // 外部冲突优先级高于内部冲突
      items[idx]._conflictType = 'external'
      items[idx]._conflictInfo = c.overlap || (c.conflict_trip ? `与"${c.conflict_trip.title}"冲突` : '时段冲突')
    }
  })
}

/** Step 0 → Step 1: 调用 AI 生成 */
async function handleGenerate() {
  const valid = await paramFormRef.value.validate().catch(() => false)
  if (!valid) return

  generating.value = true
  try {
    const payload = {
      city: params.city,
      start_date: params.start_date,
      end_date: params.end_date,
      preferences: params.preferences,
    }
    if (params.budget && params.budget > 0) {
      payload.budget = params.budget
    }

    const res = await planTrip(payload)
    const { plan, conflicts } = res.data.data

    // 为每个 item 附加前端标记
    planItems.value = plan.map((item, idx) => ({
      ...item,
      _key: `plan-${idx}-${Date.now()}`,
      _deleted: false,
      _editing: false,
      _conflictType: null,
      _conflictInfo: '',
    }))

    // 检测冲突
    detectInternalConflicts(planItems.value)
    markExternalConflicts(planItems.value, conflicts)

    step.value = 1
    ElMessage.success(`AI 已生成 ${plan.length} 条行程`)
  } catch (err) {
    const msg = err.response?.data?.message || 'AI 生成失败，请重试'
    ElMessage.error(msg)
  } finally {
    generating.value = false
  }
}

/** 切换行展开编辑 */
function toggleEdit(item) {
  if (item._deleted) return
  item._editing = !item._editing
}

/** 删除单条行程 */
function removeItem(item) {
  item._deleted = true
  item._editing = false
}

/** Step 1 → Step 2 */
function goToConfirm() {
  saveResult.value = null
  step.value = 2
}

/** Step 2: 批量保存 */
async function handleSave() {
  const toSave = planItems.value.filter((i) => !i._deleted && i._conflictType !== 'external')

  if (toSave.length === 0) {
    ElMessage.warning('没有可保存的行程')
    saveResult.value = { saved: 0, failed: activeCount.value }
    return
  }

  saving.value = true
  let saved = 0
  const failed = planItems.value.filter((i) => !i._deleted && i._conflictType === 'external').length

  for (const item of toSave) {
    try {
      await createTrip({
        city: params.city,
        date: item.date,
        start_time: item.start_time,
        end_time: item.end_time,
        title: item.title,
        description: item.description || '',
        budget: item.budget || 0,
      })
      saved++
    } catch (err) {
      // 后端冲突检测兜底
      if (err.response?.status === 409) {
        failed++
      }
    }
  }

  saveResult.value = { saved, failed }
  saving.value = false

  if (saved > 0) {
    ElMessage.success(`成功保存 ${saved} 条行程`)
    emit('saved')
  }
}
</script>

<style scoped>
/* ===== 步骤条 ===== */
.plan-steps {
  margin: var(--spacing-lg) 24px;
}

.plan-step-content {
  min-height: 320px;
  max-height: 480px;
  overflow-y: auto;
  padding: 0 4px;
}

.plan-step-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

/* ===== Step 1: 预览 ===== */
.plan-empty {
  padding: var(--spacing-xl) 0;
}

.plan-group {
  margin-bottom: var(--spacing-md);
}

.plan-group__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.plan-group__date {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.plan-group__count {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 行程卡片 */
.plan-item {
  margin-bottom: 6px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  transition: var(--transition-fast);
}

.plan-item--internal-conflict {
  background: #FFF8E1;
  border-color: #F0C06D;
}

.plan-item--external-conflict {
  background: #FFEBEE;
  border-color: #E57373;
}

.plan-item--deleted {
  opacity: 0.35;
  pointer-events: none;
}

.plan-item__summary {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 8px var(--spacing-md);
  cursor: pointer;
  user-select: none;
}

.plan-item__time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  min-width: 130px;
}

.plan-item__title {
  flex: 1;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
}

.plan-item__budget {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-accent);
  white-space: nowrap;
}

.plan-item__conflict-tag {
  flex-shrink: 0;
}

/* 展开编辑面板 */
.plan-item__edit {
  padding: 0 var(--spacing-md) var(--spacing-md);
  border-top: 1px dashed var(--border-color);
  margin-top: 4px;
  padding-top: var(--spacing-sm);
}

.plan-item__label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.plan-item__edit-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

/* 图例 */
.plan-legend {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.plan-legend__internal {
  color: #F0A020;
}

.plan-legend__external {
  color: #E57373;
}

/* ===== Step 2: 确认保存 ===== */
.plan-confirm__summary {
  text-align: center;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-md);
}

.plan-confirm__summary p {
  margin: 4px 0;
}

.plan-confirm__warn {
  color: #E57373;
}

.plan-confirm__note {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.plan-confirm__list {
  max-height: 280px;
  overflow-y: auto;
}

.plan-confirm__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 6px var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.plan-confirm__item--skip {
  opacity: 0.55;
}

.plan-confirm__check {
  flex-shrink: 0;
}

.plan-confirm__item-date {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  min-width: 90px;
}

.plan-confirm__item-title {
  flex: 1;
  font-size: var(--font-size-md);
}

.plan-confirm__item-reason {
  font-size: var(--font-size-sm);
  color: #E57373;
}

.plan-confirm__result {
  margin-top: var(--spacing-md);
}
</style>
