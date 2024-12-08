<template>
  <div>
    <!-- 显示 5 个房间的信息 -->
    <div v-for="(room, index) in rooms" :key="index" class="room-container">
      <h3>房间 {{ index + 1 }}</h3>

      <!-- 房间开关空调 -->
      <el-form ref="form1" :model="room" inline>
        <el-form-item label="房间号">
          <el-input v-model="room.roomNumber" type="number" placeholder="请输入房间号" style="width: 200px;" disabled></el-input>
        </el-form-item>
        <el-form-item>
          <el-button :class="room.isPoweredOn ? 'button-on' : 'button-off'" @click="togglePower(index)">
            {{ room.isPoweredOn ? '关闭空调' : '开启空调' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 设置目标温度 -->
      <el-form ref="form2" :model="room" inline>
        <el-form-item label="目标温度">
          <el-input v-model="room.targetTemperature" type="number" :min="room.minTemperature" :max="room.maxTemperature" placeholder="请输入目标温度" style="width: 200px;"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="setTemperatureAction(index)">设置</el-button>
        </el-form-item>
      </el-form>

      <!-- 设置风速 -->
      <el-form ref="form3" :model="room" inline>
        <el-form-item label="设置风速">
          <el-select v-model="room.windSpeed" placeholder="请选择" style="width: 200px;">
            <el-option label="Low" value="Low"></el-option>
            <el-option label="Medium" value="Medium"></el-option>
            <el-option label="High" value="High"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="setWindSpeedAction(index)">设置</el-button>
        </el-form-item>
      </el-form>

      <!-- 设置空调模式 -->
      <el-form ref="form4" :model="room" inline>
        <el-form-item label="空调模式">
          <el-select v-model="room.mode" @change="handleModeChange(index)" style="width: 200px;">
            <el-option label="Cooling" value="Cooling"></el-option>
            <el-option label="Heating" value="Heating"></el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 显示当前温度，目标温度，风速和开关机状态 -->
      <p>当前温度: {{ room.currentTemperature.toFixed(2) }} °C</p>
      <p>目标温度: {{ room.targetTemperature }} °C</p>
      <p>当前风速: {{ room.windSpeed }}</p>
      <p>空调状态: {{ room.isPoweredOn ? '开机' : '关机' }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      rooms: [
        { roomNumber: 101, isPoweredOn: false, currentTemperature: 32, targetTemperature: 25, mode: 'Cooling', windSpeed: 'Medium', minTemperature: 18, maxTemperature: 28 },
        { roomNumber: 102, isPoweredOn: false, currentTemperature: 28, targetTemperature: 25, mode: 'Cooling', windSpeed: 'Medium', minTemperature: 18, maxTemperature: 28 },
        { roomNumber: 103, isPoweredOn: false, currentTemperature: 30, targetTemperature: 25, mode: 'Cooling', windSpeed: 'Medium', minTemperature: 18, maxTemperature: 28 },
        { roomNumber: 104, isPoweredOn: false, currentTemperature: 29, targetTemperature: 25, mode: 'Cooling', windSpeed: 'Medium', minTemperature: 18, maxTemperature: 28 },
        { roomNumber: 105, isPoweredOn: false, currentTemperature: 35, targetTemperature: 25, mode: 'Cooling', windSpeed: 'Medium', minTemperature: 18, maxTemperature: 28 }
      ]
    };
  },
  methods: {
    togglePower(index) {
      const room = this.rooms[index];
      if (room.isPoweredOn) {
        axios.post('http://localhost:8000/api/turnOff', { room_number: room.roomNumber })
          .then(response => {
            room.isPoweredOn = false;
          });
      } else {
        axios.post('http://localhost:8000/api/turnOn', { room_number: room.roomNumber })
          .then(response => {
            room.isPoweredOn = true;
          });
      }
    },
    setTemperatureAction(index) {
      const room = this.rooms[index];
      axios.post('http://localhost:8000/api/set_temperature', { room_number: room.roomNumber, target_temperature: room.targetTemperature })
        .then(response => {
          console.log(response.data);
        });
    },
    setWindSpeedAction(index) {
      const room = this.rooms[index];
      axios.post('http://localhost:8000/api/set_wind_speed', { room_number: room.roomNumber, wind_speed: room.windSpeed })
        .then(response => {
          console.log(response.data);
        });
    },
    handleModeChange(index) {
      const room = this.rooms[index];
      axios.post('http://localhost:8000/api/set_mode', { room_number: room.roomNumber, mode: room.mode })
        .then(response => {
          console.log(response.data);
        });
    },
    updateRoomData() {
      axios.get('http://localhost:8000/api/room_info')
        .then(response => {
          this.rooms = response.data;
        });
    }
  },
  mounted() {
    // 获取数据并更新界面
    this.updateRoomData();

    // 每10秒更新一次房间数据
    setInterval(() => {
      this.updateRoomData();
    }, 10000);  // 10000ms = 10秒
  }
};
</script>

<style scoped>
/* 按钮样式 */
.button-on {
  background-color: #4CAF50;
  color: white;
  border-radius: 5px;
  padding: 10px 20px;
  font-size: 16px;
  transition: background-color 0.3s ease;
}
.button-on:hover {
  background-color: #45a049;
}
.button-off {
  background-color: #F44336;
  color: white;
  border-radius: 5px;
  padding: 10px 20px;
  font-size: 16px;
  transition: background-color 0.3s ease;
}
.button-off:hover {
  background-color: #e53935;
}

/* 房间容器 */
.room-container {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}
.room-container:hover {
  transform: scale(1.02);
}

/* 头部样式 */
.room-container h3 {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 15px;
  color: #333;
  text-align: center;
}

/* 表单项容器 */
.el-form-item {
  margin-bottom: 15px;
}

/* 输入框样式 */
.el-input, .el-select {
  border-radius: 5px;
  padding: 10px;
  font-size: 14px;
  width: 100%;
  margin-top: 5px;
}

/* 按钮布局和间距 */
.el-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 5px;
  margin-top: 10px;
}

/* 按钮颜色 */
.el-button--primary {
  background-color: #007BFF;
  color: white;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}
.el-button--primary:hover {
  background-color: #0056b3;
}

/* 显示信息的文本 */
.room-container div p {
  font-size: 14px;
  color: #555;
  margin: 5px 0;
}

/* 温控范围显示 */
.room-container div p:nth-child(5) {
  font-weight: bold;
  color: #333;
}

/* 布局调整 */
.el-form {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
}

/* 小屏幕设备样式 */
@media (max-width: 768px) {
  .el-form {
    flex-direction: column;
  }
  .el-input, .el-select, .el-button {
    width: 100%;
  }
  .room-container {
    padding: 15px;
  }
}
</style>
