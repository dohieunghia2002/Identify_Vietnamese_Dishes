<template>
  <div class="home">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1 class="heading">HỆ THỐNG NHẬN DẠNG MÓN ĂN ĐẶC SẢN VIỆT NAM</h1>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-btn variant="flat" color="blue-darken-4" @click="clickInput()">
            Upload hình ảnh
          </v-btn>

          <input type="file" id="upload" accept="image/png, image/jpeg, image/jpg" hidden @change="displayUploadImg()">

          <v-btn class="btn--recognize" variant="flat" color="green-accent-4" @click="recognizeImg()">
            <span>Nhận dạng</span>
          </v-btn>

          <div class="img__wrapper">
            <img class="img" src="../assets/logo_ctu.png" alt="ảnh upload">
          </div>
        </v-col>
        <v-col cols="6" class="result-detect__wrapper">
          <h2>Các thành phần nguyên liệu gồm:</h2>

          <div class="detect_result">
            <h4>YOLOV8:</h4>
            <p>{{ yolov8_detected_ingre }} => <strong>{{ v8_predicted_food }}</strong></p>
          </div>
          <div class="detect_result">
            <h4>YOLOV9:</h4>
            <p>{{ yolov9_detected_ingre }} => <strong>{{ v9_predicted_food }}</strong></p>
          </div>
          <div class="detect_result">
            <h4>YOLOV10:</h4>
            <p>{{ yolov10_detected_ingre }} => <strong>{{ v10_predicted_food }}</strong></p>
          </div>
          <div class="detect_result">
            <h4>RT-DETR:</h4>
            <p>{{ rtdetr_detected_ingre }} => <strong>{{ rtdetr_predicted_food }}</strong></p>
          </div>
        </v-col>
      </v-row>

      <v-row style="margin-top: 2rem;">
        <v-col cols="1">
          <h4>YOLOV8:</h4>
        </v-col>
        <v-col cols="1" v-for="(cropped, index) in v8_detected_img" :key="index">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + cropped" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="1">
          <h4>YOLOV9:</h4>
        </v-col>
        <v-col cols="1" v-for="(imgCropped, idx) in v9_detected_img" :key="idx">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + imgCropped" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="1">
          <h4>YOLOV10:</h4>
        </v-col>
        <v-col cols="1" v-for="(imgCropped, idx) in v10_detected_img" :key="idx">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + imgCropped" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="1">
          <h4>RT-DETR:</h4>
        </v-col>
        <v-col cols="1" v-for="(img, i) in rtdetr_detected_img" :key="i">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + img" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>


      <v-row v-if="v8_distances.length > 0" :key="v8_distances.length">
        <v-col cols="12">
          <v-table class="border border-1 border-solid" theme="light">
            <thead>
              <tr>
                <th class="text-left"></th>
                <th class="text-left">Name</th>
                <th class="text-center">YOLOV8</th>
                <th class="text-center">YOLOV9</th>
                <th class="text-center">YOLOV10</th>
                <th class="text-center">RT-DETR</th>
                <th class="text-center">Max</th>
                <th class="text-center">Sum</th>
                <th class="text-center">Gmax</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in dishesStore.dishesName" :key="idx">
                <td>{{ (idx + 1) }}</td>
                <td>{{ item }}</td>
                <td class="text-center v8--distance">{{ v8_distances[idx] }}</td>
                <td class="text-center v9--distance">{{ v9_distances[idx] }}</td>
                <td class="text-center v10--distance">{{ v10_distances[idx] }}</td>
                <td class="text-center rtdetr--distance">{{ rtdetr_distances[idx] }}</td>
                <td class="text-center max">{{ max_list[idx] }}</td>
                <td class="text-center">{{ sum_list[idx] }}</td>
                <td class="text-center">{{ Gmax[idx] }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from 'axios';
import { useDishesStore } from '../stores/dishes.js';

export default {
  setup() {
    const dishesStore = useDishesStore();
    return {
      dishesStore
    }
  },
  data() {
    return {
      yolov8_detected_cls: [],
      yolov9_detected_cls: [],
      yolov10_detected_cls: [],
      rtdetr_detected_cls: [],

      yolov8_detected_ingre: "",
      yolov9_detected_ingre: "",
      yolov10_detected_ingre: "",
      rtdetr_detected_ingre: "",

      v8_distances: [],
      v9_distances: [],
      v10_distances: [],
      rtdetr_distances: [],

      max_list: [],
      sum_list: [],
      Gmax: [],

      v8_predicted_food: "",
      v9_predicted_food: "",
      v10_predicted_food: "",
      rtdetr_predicted_food: "",

      v8_detected_img: [],
      v9_detected_img: [],
      v10_detected_img: [],
      rtdetr_detected_img: []
    }
  },

  methods: {
    async displayUploadImg() {
      const inputElement = document.getElementById("upload");
      const file = inputElement.files[0];
      const imgElement = document.getElementsByClassName("img")[0];
      imgElement.src = URL.createObjectURL(file)
    },

    async clickInput() {
      const inputElement = document.getElementById("upload");
      inputElement.click();
    },

    convertIdx2Name() {
      const v8 = this.yolov8_detected_cls.map(index => this.dishesStore.ingredients[index]);
      const v9 = this.yolov9_detected_cls.map(idx => this.dishesStore.ingredients[idx]);
      const v10 = this.yolov10_detected_cls.map(idx => this.dishesStore.ingredients[idx]);
      const rt_detr = this.rtdetr_detected_cls.map(i => this.dishesStore.ingredients[i]);

      this.yolov8_detected_ingre = v8.join(", ");
      this.yolov9_detected_ingre = v9.join(", ");
      this.yolov10_detected_ingre = v10.join(", ");
      this.rtdetr_detected_ingre = rt_detr.join(", ");
    },

    async recognizeImg() {
      const inputElement = document.getElementById("upload");
      const file = inputElement.files[0];

      const form = new FormData()
      form.append('file', file)
      const res = await axios.post('http://127.0.0.1:9999/api/predict', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      this.yolov8_detected_cls = await res.data.yolov8_detected_cls;
      this.yolov9_detected_cls = await res.data.yolov9_detected_cls;
      this.yolov10_detected_cls = await res.data.yolov10_detected_cls;
      this.rtdetr_detected_cls = await res.data.rtdetr_detected_cls;

      this.v8_distances = await res.data.v8_distances;
      this.v9_distances = await res.data.v9_distances;
      this.v10_distances = await res.data.v10_distances;
      this.rtdetr_distances = await res.data.rtdetr_distances;

      this.convertIdx2Name();

      this.max_list = await res.data.max_list;
      this.sum_list = await res.data.sum_list;
      this.Gmax = await res.data.Gmax;

      const v8_predicted_food_temp = await res.data.v8_predicted_food;
      const v9_predicted_food_temp = await res.data.v9_predicted_food;
      const v10_predicted_food_temp = await res.data.v10_predicted_food;
      const rtdetr_predicted_food_temp = await res.data.rtdetr_predicted_food;

      this.v8_predicted_food = await v8_predicted_food_temp.join(', ');
      this.v9_predicted_food = await v9_predicted_food_temp.join(', ');
      this.v10_predicted_food = await v10_predicted_food_temp.join(', ');
      this.rtdetr_predicted_food = await rtdetr_predicted_food_temp.join(', ');

      this.v8_detected_img = await res.data.v8_detected_img;
      this.v9_detected_img = await res.data.v9_detected_img;
      this.v10_detected_img = await res.data.v10_detected_img;
      this.rtdetr_detected_img = await res.data.rtdetr_detected_img;

    }
  }
}
</script>

<style>
.heading {
  text-align: center;
  color: rgb(247, 37, 37);
}

.btn--recognize {
  margin-left: 20px;
}

.btn--recognize span {
  color: aliceblue;
}

.img__wrapper {
  margin-top: 2rem;
  width: 65%;
}

.img,
.img--cropped {
  width: 100%;
}

.detect_result {
  margin-top: 1rem;
}

.result-detect__wrapper {
  background-color: rgb(243, 242, 236);
}
</style>