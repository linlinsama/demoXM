package com.example.demoXM.Dao;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

import com.example.demoXM.entity.Hoken;

@Mapper
public interface HokenDao {

	//根据男女+贩卖区分+ステータス筛选出能显示的保险数量
	public List<Hoken> getHoken(String sex);

	//在保险情报搜索里展示出公司所拥有的所有保险
	public List<Hoken> showall();


	//通过条件 在保险情报搜索页面里搜索
	public List<Hoken> selectHoken(String HKID, String HKN,String HKKTKB,String HBKB,String STS);
}
