<template>
    <div class="row my-3">
        <div class="col-12 col-md-12 col-lg-8">
            <div class="card">
                <div class="card-body p-3">
                    <!-- Горизонтальный контейнер -->
                    <div class="d-flex align-items-center">
                        <!-- Кружок с уровнем, цвет зависит от уровня -->
                        <div
                            class="rounded-circle text-white d-flex align-items-center justify-content-center"
                            :class="levelCircleClass"
                            style="width: 40px; height: 40px; font-size: 1.2rem;"
                        >
                            {{ level }}
                        </div>

                        <!-- Прогресс и подписи справа -->
                        <div class="flex-grow-1 ms-3">
                            <!-- Прогресс-бар (всегда от 0 до 100) -->
                            <div class="progress mt-2" style="height: 20px;">
                                <div
                                    class="progress-bar bg-success progress-bar-striped"
                                    role="progressbar"
                                    :style="{ width: approvedPercent + '%' }"
                                >
                                    {{ chunkApproved + ' / ' + chunkSize }} (подтв.)
                                </div>
                                <div
                                    class="progress-bar bg-warning progress-bar-striped"
                                    role="progressbar"
                                    :style="{ width: unapprovedPercent + '%' }"
                                >
                                    {{ chunkUnapproved }} (неподтв.)
                                </div>
                            </div>

                            <!-- Текстовое описание -->
                            <small class="text-muted">
                                Всего баллов: {{ totalPoints }}
                                •
                                В текущем уровне {{ deltaPoints }} из {{ chunkSize }}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import useMainStore from "@/stores/mainStore.js";
import {canFillInCategory} from "@/utils/access.js";

export default {
    name: "PortfolioGamificationWidget",

    props: {
        object: {type: Object, required: true}
    },

    data() {
        return {
            // «Цена» каждого типа в баллах
            pointsMap: {
                submission: 10,
                projects: 30,
                events: 10
            },
            relativesTypes: ['projects', 'events'],
            store: useMainStore()
        };
    },

    computed: {
        /**
         * Собираем все записи (из _submissions и _relatives) в единый массив,
         * чтобы в дальнейшем легко считать общие и подтверждённые баллы.
         */
        allRecords() {
            const records = [];

            // _submissions считаем как type = "submission"
            if (Array.isArray(this.object._submissions)) {
                for (const s of this.object._submissions) {
                    if (canFillInCategory(this.store.getFormCategory(s._form.category_id))) {
                        records.push({
                            type: "submission",
                            approved: !!s.is_approved
                        });
                    }

                }
            }

            // _relatives (projects, events и т.п.)
            for (const relType of this.relativesTypes) {
                for (let rel of this.findRelativesByType(relType)) {
                    records.push({
                        type: rel.type,
                        approved: !!rel.is_approved
                    });
                }
            }
            return records;
        },

        // Разделяем записи на подтверждённые / неподтверждённые
        approvedRecords() {
            return this.allRecords.filter(r => r.approved);
        },
        unapprovedRecords() {
            return this.allRecords.filter(r => !r.approved);
        },

        // Подсчёт баллов
        approvedPoints() {
            return this.approvedRecords.reduce(
                (sum, r) => sum + (this.pointsMap[r.type] || 0),
                0
            );
        },
        unapprovedPoints() {
            return this.unapprovedRecords.reduce(
                (sum, r) => sum + (this.pointsMap[r.type] || 0),
                0
            );
        },
        totalPoints() {
            return this.approvedPoints + this.unapprovedPoints;
        },

        // Каждые 100 баллов — новый уровень
        level() {
            return Math.floor(this.totalPoints / 100) + 1;
        },
        currentLevelStart() {
            return Math.floor(this.totalPoints / 100) * 100;
        },

        // Сколько баллов набрано в текущем уровне
        deltaPoints() {
            return this.totalPoints - this.currentLevelStart;
        },
        chunkSize() {
            return 100;
        },

        // Подтверждённые очки в пределах 0..100
        chunkApproved() {
            let raw = this.approvedPoints - this.currentLevelStart;
            if (raw < 0) raw = 0;
            if (raw > this.chunkSize) raw = this.chunkSize;
            if (raw > this.deltaPoints) raw = this.deltaPoints;
            return raw;
        },
        // Неподтверждённые очки внутри текущего уровня
        chunkUnapproved() {
            return this.deltaPoints - this.chunkApproved;
        },

        // Для прогресс-бара в процентах
        approvedPercent() {
            return (this.chunkApproved / this.chunkSize) * 100;
        },
        unapprovedPercent() {
            return (this.chunkUnapproved / this.chunkSize) * 100;
        },

        /**
         * Динамический класс для кружка с уровнем.
         * Можно задавать более тонкую логику (например, разные цвета каждые несколько уровней).
         */
        levelCircleClass() {
            // Пример:
            // - уровни 1-2: bg-secondary
            // - уровни 3-5: bg-primary
            // - уровни 6-9: bg-info
            // - 10+: bg-danger
            if (this.level <= 1) {
                return "bg-info";
            } else if (this.level < 3) {
                return "bg-success";
            } else if (this.level < 6) {
                return "bg-primary";
            } else {
                return "bg-danger";
            }
        }
    },

    methods: {
        /**
         * Вспомогательный метод для поиска объектов по типу,
         * если необходимо работать именно с _relatives (не включая сабмишены).
         */
        findRelativesByType(type) {
            const relatives = [
                ...this.object.children.filter((child) => child.type === type),
                ...this.object.parents.filter((parent) => parent.type === type)
            ].map(relative => this.store.getObject(relative.type, relative.id));

            return relatives.sort((a, b) => a.name.localeCompare(b.name));
        }
    }
};
</script>

<style scoped>
/* При необходимости переопределяйте стили, здесь для примера используется Bootstrap */
</style>