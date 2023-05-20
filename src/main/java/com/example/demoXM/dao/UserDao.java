package com.example.demoXM.dao;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserDao {
	//得到是社员还是会员
	public String getuserwake(String lOGINN,String PASS);

}
