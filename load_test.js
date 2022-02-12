import http from 'k6/http';
import { sleep } from 'k6';
export const options = {
  vus: 10000,
  duration: '30s',
};
export default function () {
  http.get('http://127.0.0.1:8000/deliveries/cost?province=Jawa%20Timur&city=Surabaya&district=Sukolilo&weight=1000');
  http.get('http://127.0.0.1:8000/deliveries/cost?province=Kepulauan%20Riau&city=Batam&district=Batam%20Kota&weight=1000');
  sleep(1);
}
