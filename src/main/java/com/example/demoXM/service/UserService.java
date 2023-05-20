package com.example.demoXM.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demoXM.dao.UserDao;

@Service
public class UserService {
	@Autowired
	private UserDao userDao;

	//查询是会员还是社员
	public String getuserwake(String lOGINN,String PASS) {
		return	userDao.getuserwake(lOGINN, PASS);

	}

}
