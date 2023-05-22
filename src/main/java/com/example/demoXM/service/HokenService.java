package com.example.demoXM.service;

import java.util.Date;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demoXM.dao.HokenDao;
import com.example.demoXM.entity.Hoken;
import com.example.demoXM.entity.User;

@Service
public class HokenService {
	@Autowired
	private HokenDao hokenDao;

	//查询
	public List<Hoken> getHoken(String sex){
		List<Hoken> result=hokenDao.getHoken(sex);
		return hokenDao.getHoken(sex);
	}

//	//在页面里展示所有
//	public List<Hoken>showall(){
//		return hokenDao.showall();
//	}

	//按条件查询
	public List<Hoken>selectHoken(String HKID, String HKN,String HKKTKB,String HBKB,String STS){
		return hokenDao.selectHoken(HKID, HKN, HKKTKB,HBKB,STS);
	}

	//添加
	public int addHoken(Hoken hoken, User user) {
		hoken.setINSERTID(user.getlOGINN());
		hoken.setUPDATEID(user.getlOGINN());
		Date date=new Date();
		hoken.setINSERTDTE(date);
		hoken.setUPDATEDTE(date);
		return hokenDao.addHoken(hoken);
	}
	//通过id找全部
	public List<Hoken>selectId(String HKID){
		return hokenDao.selectId(HKID);
	}

}
