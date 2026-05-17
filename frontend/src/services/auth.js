import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const registerUser = async (userData) => {

  return axios.post(
    `${API_URL}/user/register`,
    userData
  );
};

export const loginUser = async (userData) => {

  return axios.post(
    `${API_URL}/user/login`,
    userData
  );
};