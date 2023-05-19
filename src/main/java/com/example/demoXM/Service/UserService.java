package com.example.demoXM.Service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demoXM.Dao.UserDao;

@Service
public class UserService {
	@Autowired
	private UserDao userDao;

	//查询是会员还是社员
	public String getuserwake(String lOGINN,String PASS) {
		return	userDao.getuserwake(lOGINN, PASS);

	}

}
