package com.example.demoXM.Service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.demoXM.Dao.HokenDao;
import com.example.demoXM.entity.Hoken;

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

}
