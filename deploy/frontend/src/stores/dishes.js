import { defineStore } from 'pinia';

export const useDishesStore = defineStore('dishes', {
    state: () => {
        return {
            ingredients: ['cá', 'bún', 'hủ tiếu', 'tôm', 'thịt heo', 'gan', 'thịt heo quay', 'thịt bò', 'trứng',
                'thịt bằm', 'tôm tít', 'mực', 'viên mọc', 'bánh hỏi', 'dưa chua', 'phở', 'cơm', 'sườn', 'bì', 'thịt gà',
                'rau răm', 'mì', 'bánh đa', 'chả cốm', 'dồi sụn', 'đậu hủ', 'chả giò'],
            dishesName: ["Bún cá", "Hủ tiếu Mỹ Tho", "Bún nước lèo", "Cơm tấm Long Xuyên",
                "Bún hải sản bề bề", "Bánh hỏi heo quay", "Cơm gà", "Cao lầu", "Mì Quảng", "Bún bò Huế", "Phở Hà Nội",
                "Bún mực", "Bún mọc", "Bún đậu mắm tôm"]
        }
    }
})