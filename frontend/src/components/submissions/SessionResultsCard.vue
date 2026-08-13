<template>
  <div class="session-results">
    <div v-if="periodValue || averageScore !== null" class="session-summary">
      <span v-if="periodValue" class="session-period">{{ periodValue }}</span>
      <span v-if="averageScore !== null" class="session-average">
        Средний балл <strong>{{ formatScore(averageScore) }}</strong>
      </span>
    </div>

    <div v-if="scoreEntries.length" class="session-score-list">
      <div v-for="([name, score]) in scoreEntries" :key="name" class="session-score-row">
        <span class="session-subject">{{ name }}</span>
        <span class="session-score" :class="scoreClass(score)">{{ formatScore(score) }}</span>
      </div>
    </div>

    <ShowoffPresenter
      v-if="otherAttributes.length"
      class="session-other-attributes"
      :attributes="otherAttributesObject"
    />
  </div>
</template>

<script>
import ShowoffPresenter from '@/components/submissions/ShowoffPresenter.vue';

const PERIOD_FIELDS = new Set(['период']);

export default {
  name: 'SessionResultsCard',
  components: {ShowoffPresenter},
  props: {
    attributes: {
      type: Object,
      default: () => ({}),
    },
    hiddenAttributes: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    visibleEntries() {
      return Object.entries(this.attributes || {})
        .filter(([name]) => !this.hiddenAttributes.includes(name));
    },
    periodEntry() {
      return this.visibleEntries.find(([name]) => PERIOD_FIELDS.has(name.trim().toLowerCase()));
    },
    periodValue() {
      return this.periodEntry?.[1] || '';
    },
    scoreEntries() {
      return this.visibleEntries
        .filter(([name, value]) => !PERIOD_FIELDS.has(name.trim().toLowerCase()) && this.numericScore(value) !== null)
        .map(([name, value]) => [name, this.numericScore(value)]);
    },
    averageScore() {
      if (!this.scoreEntries.length) return null;
      return this.scoreEntries.reduce((sum, [, score]) => sum + score, 0) / this.scoreEntries.length;
    },
    otherAttributes() {
      return this.visibleEntries.filter(([name, value]) => (
        !PERIOD_FIELDS.has(name.trim().toLowerCase()) && this.numericScore(value) === null
      ));
    },
    otherAttributesObject() {
      return Object.fromEntries(this.otherAttributes);
    },
  },
  methods: {
    numericScore(value) {
      if (typeof value === 'number' && Number.isFinite(value)) return value;
      if (typeof value !== 'string' || !value.trim()) return null;
      const normalized = value.trim().replace(',', '.');
      if (!/^\d+(?:\.\d+)?$/.test(normalized)) return null;
      const score = Number(normalized);
      return Number.isFinite(score) ? score : null;
    },
    formatScore(value) {
      return Number.isInteger(value) ? String(value) : value.toFixed(1).replace('.', ',');
    },
    scoreClass(score) {
      if (score >= 9) return 'session-score--excellent';
      if (score >= 7) return 'session-score--good';
      if (score >= 5) return 'session-score--medium';
      return 'session-score--low';
    },
  },
};
</script>

<style scoped>
.session-results {
  display: grid;
  gap: 0.9rem;
  margin-top: 0.9rem;
}

.session-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.session-period {
  padding: 0.2rem 0.5rem;
  color: var(--silaeder-primary-dark);
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 999px;
  background: var(--silaeder-primary-soft);
}

.session-average {
  color: var(--silaeder-muted);
  font-size: 0.75rem;
}

.session-average strong {
  color: var(--silaeder-text);
  font-size: 0.9rem;
}

.session-score-list {
  display: grid;
  gap: 0.35rem;
}

.session-score-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.75rem;
  min-height: 1.7rem;
}

.session-subject {
  min-width: 0;
  font-size: 0.85rem;
  overflow-wrap: anywhere;
}

.session-score {
  display: inline-grid;
  place-items: center;
  min-width: 2rem;
  height: 1.65rem;
  padding: 0 0.4rem;
  color: #fff;
  font-size: 0.78rem;
  font-weight: 700;
  border-radius: 0.45rem;
  font-variant-numeric: tabular-nums;
}

.session-score--excellent {
  background: #2f8a63;
}

.session-score--good {
  background: var(--silaeder-primary);
}

.session-score--medium {
  color: #4a3d14;
  background: var(--silaeder-warning);
}

.session-score--low {
  background: var(--silaeder-danger);
}

.session-other-attributes {
  padding-top: 0.75rem;
  border-top: 1px solid var(--silaeder-border);
}
</style>
